"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __esm = (fn, res) => function __init() {
  return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
};
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/config.ts
var import_sdk, configSchematics;
var init_config = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/config.ts"() {
    "use strict";
    import_sdk = require("@lmstudio/sdk");
    configSchematics = (0, import_sdk.createConfigSchematics)().field(
      "retrievalLimit",
      "numeric",
      {
        int: true,
        min: 1,
        displayName: "Retrieval Limit",
        subtitle: "When retrieval is triggered, this is the maximum number of chunks to return.",
        slider: { min: 1, max: 10, step: 1 }
      },
      3
    ).field(
      "retrievalAffinityThreshold",
      "numeric",
      {
        min: 0,
        max: 1,
        displayName: "Retrieval Affinity Threshold",
        subtitle: "The minimum similarity score for a chunk to be considered relevant.",
        slider: { min: 0, max: 1, step: 0.01 }
      },
      0.5
    ).build();
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/promptPreprocessor.ts
async function preprocess(ctl, userMessage) {
  const userPrompt = userMessage.getText();
  const history = await ctl.pullHistory();
  history.append(userMessage);
  const newFiles = userMessage.getFiles(ctl.client).filter((f) => f.type !== "image");
  const files = history.getAllFiles(ctl.client).filter((f) => f.type !== "image");
  if (newFiles.length > 0) {
    const strategy = await chooseContextInjectionStrategy(ctl, userPrompt, newFiles);
    if (strategy === "inject-full-content") {
      return await prepareDocumentContextInjection(ctl, userMessage);
    } else if (strategy === "retrieval") {
      return await prepareRetrievalResultsContextInjection(ctl, userPrompt, files);
    }
  } else if (files.length > 0) {
    return await prepareRetrievalResultsContextInjection(ctl, userPrompt, files);
  }
  return userMessage;
}
async function prepareRetrievalResultsContextInjection(ctl, originalUserPrompt, files) {
  const pluginConfig = ctl.getPluginConfig(configSchematics);
  const retrievalLimit = pluginConfig.get("retrievalLimit");
  const retrievalAffinityThreshold = pluginConfig.get("retrievalAffinityThreshold");
  const statusSteps = /* @__PURE__ */ new Map();
  const retrievingStatus = ctl.createStatus({
    status: "loading",
    text: `Loading an embedding model for retrieval...`
  });
  const model = await ctl.client.embedding.model("nomic-ai/nomic-embed-text-v1.5-GGUF", {
    signal: ctl.abortSignal
  });
  retrievingStatus.setState({
    status: "loading",
    text: `Retrieving relevant citations for user query...`
  });
  const result = await ctl.client.files.retrieve(originalUserPrompt, files, {
    embeddingModel: model,
    // Affinity threshold: 0.6 not implemented
    limit: retrievalLimit,
    signal: ctl.abortSignal,
    onFileProcessList(filesToProcess) {
      for (const file of filesToProcess) {
        statusSteps.set(
          file,
          retrievingStatus.addSubStatus({
            status: "waiting",
            text: `Process ${file.name} for retrieval`
          })
        );
      }
    },
    onFileProcessingStart(file) {
      statusSteps.get(file).setState({ status: "loading", text: `Processing ${file.name} for retrieval` });
    },
    onFileProcessingEnd(file) {
      statusSteps.get(file).setState({ status: "done", text: `Processed ${file.name} for retrieval` });
    },
    onFileProcessingStepProgress(file, step, progressInStep) {
      const verb = step === "loading" ? "Loading" : step === "chunking" ? "Chunking" : "Embedding";
      statusSteps.get(file).setState({
        status: "loading",
        text: `${verb} ${file.name} for retrieval (${(progressInStep * 100).toFixed(1)}%)`
      });
    }
  });
  result.entries = result.entries.filter((entry) => entry.score > retrievalAffinityThreshold);
  let processedContent = "";
  const numRetrievals = result.entries.length;
  if (numRetrievals > 0) {
    retrievingStatus.setState({
      status: "done",
      text: `Retrieved ${numRetrievals} relevant citations for user query`
    });
    ctl.debug("Retrieval results", result);
    const prefix = "The following citations were found in the files provided by the user:\n\n";
    processedContent += prefix;
    let citationNumber = 1;
    result.entries.forEach((result2) => {
      const completeText = result2.content;
      processedContent += `Citation ${citationNumber}: "${completeText}"

`;
      citationNumber++;
    });
    await ctl.addCitations(result);
    const suffix = `Use the citations above to respond to the user query, only if they are relevant. Otherwise, respond to the best of your ability without them.

User Query:

${originalUserPrompt}`;
    processedContent += suffix;
  } else {
    retrievingStatus.setState({
      status: "canceled",
      text: `No relevant citations found for user query`
    });
    ctl.debug("No relevant citations found for user query");
    const noteAboutNoRetrievalResultsFound = `Important: No citations were found in the user files for the user query. In less than one sentence, inform the user of this. Then respond to the query to the best of your ability.`;
    processedContent = noteAboutNoRetrievalResultsFound + `

User Query:

${originalUserPrompt}`;
  }
  ctl.debug("Processed content", processedContent);
  return processedContent;
}
async function prepareDocumentContextInjection(ctl, input) {
  const documentInjectionSnippets = /* @__PURE__ */ new Map();
  const files = input.consumeFiles(ctl.client, (file) => file.type !== "image");
  for (const file of files) {
    const { content } = await ctl.client.files.parseDocument(file, {
      signal: ctl.abortSignal
    });
    ctl.debug(import_sdk2.text`
      Strategy: inject-full-content. Injecting full content of file '${file}' into the
      context. Length: ${content.length}.
    `);
    documentInjectionSnippets.set(file, content);
  }
  let formattedFinalUserPrompt = "";
  if (documentInjectionSnippets.size > 0) {
    formattedFinalUserPrompt += "This is a Enriched Context Generation scenario.\n\nThe following content was found in the files provided by the user.\n";
    for (const [fileHandle, snippet] of documentInjectionSnippets) {
      formattedFinalUserPrompt += `

** ${fileHandle.name} full content **

${snippet}

** end of ${fileHandle.name} **

`;
    }
    formattedFinalUserPrompt += `Based on the content above, please provide a response to the user query.

User query: ${input.getText()}`;
  }
  input.replaceText(formattedFinalUserPrompt);
  return input;
}
async function getEffectiveContextFormatted(ctx, model, ctl) {
  try {
    return await model.applyPromptTemplate(ctx);
  } catch (e) {
    const hasAnyUserMessage = ctx.getMessagesArray().some((message) => message.getRole() === "user");
    if (!hasAnyUserMessage) {
      const placeholderUserMessageContent = "?";
      ctl.debug(import_sdk2.text`
        Failed to apply prompt template on context with no user messages. Retrying with placeholder
        user message.
      `);
      const measurementContext = ctx.withAppended("user", placeholderUserMessageContent);
      return await model.applyPromptTemplate(measurementContext);
    }
    throw e;
  }
}
async function measureContextWindow(ctx, model, ctl) {
  const currentContextFormatted = await getEffectiveContextFormatted(ctx, model, ctl);
  const totalTokensInContext = await model.countTokens(currentContextFormatted);
  const modelContextLength = await model.getContextLength();
  const modelRemainingContextLength = modelContextLength - totalTokensInContext;
  const contextOccupiedPercent = totalTokensInContext / modelContextLength * 100;
  return {
    totalTokensInContext,
    modelContextLength,
    modelRemainingContextLength,
    contextOccupiedPercent
  };
}
async function chooseContextInjectionStrategy(ctl, originalUserPrompt, files) {
  const status = ctl.createStatus({
    status: "loading",
    text: `Deciding how to handle the document(s)...`
  });
  const model = await ctl.client.llm.model();
  const ctx = await ctl.pullHistory();
  const {
    totalTokensInContext,
    modelContextLength,
    modelRemainingContextLength,
    contextOccupiedPercent
  } = await measureContextWindow(ctx, model, ctl);
  ctl.debug(
    `Context measurement result:

	Total tokens in context: ${totalTokensInContext}
	Model context length: ${modelContextLength}
	Model remaining context length: ${modelRemainingContextLength}
	Context occupied percent: ${contextOccupiedPercent.toFixed(2)}%
`
  );
  let totalFileTokenCount = 0;
  let totalReadTime = 0;
  let totalTokenizeTime = 0;
  for (const file of files) {
    const startTime = performance.now();
    const loadingStatus = status.addSubStatus({
      status: "loading",
      text: `Loading parser for ${file.name}...`
    });
    let actionProgressing = "Reading";
    let parserIndicator = "";
    const { content } = await ctl.client.files.parseDocument(file, {
      signal: ctl.abortSignal,
      onParserLoaded: (parser) => {
        loadingStatus.setState({
          status: "loading",
          text: `${parser.library} loaded for ${file.name}...`
        });
        if (parser.library !== "builtIn") {
          actionProgressing = "Parsing";
          parserIndicator = ` with ${parser.library}`;
        }
      },
      onProgress: (progress) => {
        loadingStatus.setState({
          status: "loading",
          text: `${actionProgressing} file ${file.name}${parserIndicator}... (${(progress * 100).toFixed(2)}%)`
        });
      }
    });
    loadingStatus.remove();
    totalReadTime += performance.now() - startTime;
    const startTokenizeTime = performance.now();
    totalFileTokenCount += await model.countTokens(content);
    totalTokenizeTime += performance.now() - startTokenizeTime;
    if (totalFileTokenCount > modelRemainingContextLength) {
      break;
    }
  }
  ctl.debug(`Total file read time: ${totalReadTime.toFixed(2)} ms`);
  ctl.debug(`Total tokenize time: ${totalTokenizeTime.toFixed(2)} ms`);
  ctl.debug(`Original User Prompt: ${originalUserPrompt}`);
  const userPromptTokenCount = (await model.tokenize(originalUserPrompt)).length;
  const totalFilePlusPromptTokenCount = totalFileTokenCount + userPromptTokenCount;
  const contextOccupiedFraction = contextOccupiedPercent / 100;
  const targetContextUsePercent = 0.7;
  const targetContextUsage = targetContextUsePercent * (1 - contextOccupiedFraction);
  const availableContextTokens = Math.floor(modelRemainingContextLength * targetContextUsage);
  ctl.debug("Strategy Calculation:");
  ctl.debug(`	Total Tokens in All Files: ${totalFileTokenCount}`);
  ctl.debug(`	Total Tokens in User Prompt: ${userPromptTokenCount}`);
  ctl.debug(`	Model Context Remaining: ${modelRemainingContextLength} tokens`);
  ctl.debug(`	Context Occupied: ${contextOccupiedPercent.toFixed(2)}%`);
  ctl.debug(`	Available Tokens: ${availableContextTokens}
`);
  if (totalFilePlusPromptTokenCount > availableContextTokens) {
    const chosenStrategy2 = "retrieval";
    ctl.debug(
      `Chosen context injection strategy: '${chosenStrategy2}'. Total file + prompt token count: ${totalFilePlusPromptTokenCount} > ${targetContextUsage * 100}% * available context tokens: ${availableContextTokens}`
    );
    status.setState({
      status: "done",
      text: `Chosen context injection strategy: '${chosenStrategy2}'. Retrieval is optimal for the size of content provided`
    });
    return chosenStrategy2;
  }
  const chosenStrategy = "inject-full-content";
  status.setState({
    status: "done",
    text: `Chosen context injection strategy: '${chosenStrategy}'. All content can fit into the context`
  });
  return chosenStrategy;
}
var import_sdk2;
var init_promptPreprocessor = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/promptPreprocessor.ts"() {
    "use strict";
    import_sdk2 = require("@lmstudio/sdk");
    init_config();
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/index.ts
var src_exports = {};
__export(src_exports, {
  main: () => main
});
async function main(context) {
  context.withConfigSchematics(configSchematics);
  context.withPromptPreprocessor(preprocess);
}
var init_src = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/src/index.ts"() {
    "use strict";
    init_config();
    init_promptPreprocessor();
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/35e18fa671a337af1834844684cefda0/.lmstudio/entry.ts
var import_sdk3 = require("@lmstudio/sdk");
var clientIdentifier = process.env.LMS_PLUGIN_CLIENT_IDENTIFIER;
var clientPasskey = process.env.LMS_PLUGIN_CLIENT_PASSKEY;
var baseUrl = process.env.LMS_PLUGIN_BASE_URL;
var client = new import_sdk3.LMStudioClient({
  clientIdentifier,
  clientPasskey,
  baseUrl
});
globalThis.__LMS_PLUGIN_CONTEXT = true;
var predictionLoopHandlerSet = false;
var promptPreprocessorSet = false;
var configSchematicsSet = false;
var globalConfigSchematicsSet = false;
var toolsProviderSet = false;
var generatorSet = false;
var selfRegistrationHost = client.plugins.getSelfRegistrationHost();
var pluginContext = {
  withPredictionLoopHandler: (generate) => {
    if (predictionLoopHandlerSet) {
      throw new Error("PredictionLoopHandler already registered");
    }
    if (toolsProviderSet) {
      throw new Error("PredictionLoopHandler cannot be used with a tools provider");
    }
    predictionLoopHandlerSet = true;
    selfRegistrationHost.setPredictionLoopHandler(generate);
    return pluginContext;
  },
  withPromptPreprocessor: (preprocess2) => {
    if (promptPreprocessorSet) {
      throw new Error("PromptPreprocessor already registered");
    }
    promptPreprocessorSet = true;
    selfRegistrationHost.setPromptPreprocessor(preprocess2);
    return pluginContext;
  },
  withConfigSchematics: (configSchematics2) => {
    if (configSchematicsSet) {
      throw new Error("Config schematics already registered");
    }
    configSchematicsSet = true;
    selfRegistrationHost.setConfigSchematics(configSchematics2);
    return pluginContext;
  },
  withGlobalConfigSchematics: (globalConfigSchematics) => {
    if (globalConfigSchematicsSet) {
      throw new Error("Global config schematics already registered");
    }
    globalConfigSchematicsSet = true;
    selfRegistrationHost.setGlobalConfigSchematics(globalConfigSchematics);
    return pluginContext;
  },
  withToolsProvider: (toolsProvider) => {
    if (toolsProviderSet) {
      throw new Error("Tools provider already registered");
    }
    if (predictionLoopHandlerSet) {
      throw new Error("Tools provider cannot be used with a predictionLoopHandler");
    }
    toolsProviderSet = true;
    selfRegistrationHost.setToolsProvider(toolsProvider);
    return pluginContext;
  },
  withGenerator: (generator) => {
    if (generatorSet) {
      throw new Error("Generator already registered");
    }
    generatorSet = true;
    selfRegistrationHost.setGenerator(generator);
    return pluginContext;
  }
};
Promise.resolve().then(() => (init_src(), src_exports)).then(async (module2) => {
  return await module2.main(pluginContext);
}).then(() => {
  selfRegistrationHost.initCompleted();
}).catch((error) => {
  console.error("Failed to execute the main function of the plugin.");
  console.error(error);
});
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vc3JjL2NvbmZpZy50cyIsICIuLi9zcmMvcHJvbXB0UHJlcHJvY2Vzc29yLnRzIiwgIi4uL3NyYy9pbmRleC50cyIsICJlbnRyeS50cyJdLAogICJzb3VyY2VzQ29udGVudCI6IFsiaW1wb3J0IHsgY3JlYXRlQ29uZmlnU2NoZW1hdGljcyB9IGZyb20gXCJAbG1zdHVkaW8vc2RrXCI7XHJcblxyXG5leHBvcnQgY29uc3QgY29uZmlnU2NoZW1hdGljcyA9IGNyZWF0ZUNvbmZpZ1NjaGVtYXRpY3MoKVxyXG4gIC5maWVsZChcclxuICAgIFwicmV0cmlldmFsTGltaXRcIixcclxuICAgIFwibnVtZXJpY1wiLFxyXG4gICAge1xyXG4gICAgICBpbnQ6IHRydWUsXHJcbiAgICAgIG1pbjogMSxcclxuICAgICAgZGlzcGxheU5hbWU6IFwiUmV0cmlldmFsIExpbWl0XCIsXHJcbiAgICAgIHN1YnRpdGxlOiBcIldoZW4gcmV0cmlldmFsIGlzIHRyaWdnZXJlZCwgdGhpcyBpcyB0aGUgbWF4aW11bSBudW1iZXIgb2YgY2h1bmtzIHRvIHJldHVybi5cIixcclxuICAgICAgc2xpZGVyOiB7IG1pbjogMSwgbWF4OiAxMCwgc3RlcDogMSB9LFxyXG4gICAgfSxcclxuICAgIDMsXHJcbiAgKVxyXG4gIC5maWVsZChcclxuICAgIFwicmV0cmlldmFsQWZmaW5pdHlUaHJlc2hvbGRcIixcclxuICAgIFwibnVtZXJpY1wiLFxyXG4gICAge1xyXG4gICAgICBtaW46IDAuMCxcclxuICAgICAgbWF4OiAxLjAsXHJcbiAgICAgIGRpc3BsYXlOYW1lOiBcIlJldHJpZXZhbCBBZmZpbml0eSBUaHJlc2hvbGRcIixcclxuICAgICAgc3VidGl0bGU6IFwiVGhlIG1pbmltdW0gc2ltaWxhcml0eSBzY29yZSBmb3IgYSBjaHVuayB0byBiZSBjb25zaWRlcmVkIHJlbGV2YW50LlwiLFxyXG4gICAgICBzbGlkZXI6IHsgbWluOiAwLjAsIG1heDogMS4wLCBzdGVwOiAwLjAxIH0sXHJcbiAgICB9LFxyXG4gICAgMC41LFxyXG4gIClcclxuICAuYnVpbGQoKTtcclxuIiwgImltcG9ydCB7XHJcbiAgdGV4dCxcclxuICB0eXBlIENoYXQsXHJcbiAgdHlwZSBDaGF0TWVzc2FnZSxcclxuICB0eXBlIEZpbGVIYW5kbGUsXHJcbiAgdHlwZSBMTE1EeW5hbWljSGFuZGxlLFxyXG4gIHR5cGUgUHJlZGljdGlvblByb2Nlc3NTdGF0dXNDb250cm9sbGVyLFxyXG4gIHR5cGUgUHJvbXB0UHJlcHJvY2Vzc29yQ29udHJvbGxlcixcclxufSBmcm9tIFwiQGxtc3R1ZGlvL3Nka1wiO1xyXG5pbXBvcnQgeyBjb25maWdTY2hlbWF0aWNzIH0gZnJvbSBcIi4vY29uZmlnXCI7XHJcblxyXG50eXBlIERvY3VtZW50Q29udGV4dEluamVjdGlvblN0cmF0ZWd5ID0gXCJub25lXCIgfCBcImluamVjdC1mdWxsLWNvbnRlbnRcIiB8IFwicmV0cmlldmFsXCI7XHJcblxyXG5leHBvcnQgYXN5bmMgZnVuY3Rpb24gcHJlcHJvY2VzcyhjdGw6IFByb21wdFByZXByb2Nlc3NvckNvbnRyb2xsZXIsIHVzZXJNZXNzYWdlOiBDaGF0TWVzc2FnZSkge1xyXG4gIGNvbnN0IHVzZXJQcm9tcHQgPSB1c2VyTWVzc2FnZS5nZXRUZXh0KCk7XHJcbiAgY29uc3QgaGlzdG9yeSA9IGF3YWl0IGN0bC5wdWxsSGlzdG9yeSgpO1xyXG4gIGhpc3RvcnkuYXBwZW5kKHVzZXJNZXNzYWdlKTtcclxuICBjb25zdCBuZXdGaWxlcyA9IHVzZXJNZXNzYWdlLmdldEZpbGVzKGN0bC5jbGllbnQpLmZpbHRlcihmID0+IGYudHlwZSAhPT0gXCJpbWFnZVwiKTtcclxuICBjb25zdCBmaWxlcyA9IGhpc3RvcnkuZ2V0QWxsRmlsZXMoY3RsLmNsaWVudCkuZmlsdGVyKGYgPT4gZi50eXBlICE9PSBcImltYWdlXCIpO1xyXG5cclxuICBpZiAobmV3RmlsZXMubGVuZ3RoID4gMCkge1xyXG4gICAgY29uc3Qgc3RyYXRlZ3kgPSBhd2FpdCBjaG9vc2VDb250ZXh0SW5qZWN0aW9uU3RyYXRlZ3koY3RsLCB1c2VyUHJvbXB0LCBuZXdGaWxlcyk7XHJcbiAgICBpZiAoc3RyYXRlZ3kgPT09IFwiaW5qZWN0LWZ1bGwtY29udGVudFwiKSB7XHJcbiAgICAgIHJldHVybiBhd2FpdCBwcmVwYXJlRG9jdW1lbnRDb250ZXh0SW5qZWN0aW9uKGN0bCwgdXNlck1lc3NhZ2UpO1xyXG4gICAgfSBlbHNlIGlmIChzdHJhdGVneSA9PT0gXCJyZXRyaWV2YWxcIikge1xyXG4gICAgICByZXR1cm4gYXdhaXQgcHJlcGFyZVJldHJpZXZhbFJlc3VsdHNDb250ZXh0SW5qZWN0aW9uKGN0bCwgdXNlclByb21wdCwgZmlsZXMpO1xyXG4gICAgfVxyXG4gIH0gZWxzZSBpZiAoZmlsZXMubGVuZ3RoID4gMCkge1xyXG4gICAgcmV0dXJuIGF3YWl0IHByZXBhcmVSZXRyaWV2YWxSZXN1bHRzQ29udGV4dEluamVjdGlvbihjdGwsIHVzZXJQcm9tcHQsIGZpbGVzKTtcclxuICB9XHJcblxyXG4gIHJldHVybiB1c2VyTWVzc2FnZTtcclxufVxyXG5cclxuYXN5bmMgZnVuY3Rpb24gcHJlcGFyZVJldHJpZXZhbFJlc3VsdHNDb250ZXh0SW5qZWN0aW9uKFxyXG4gIGN0bDogUHJvbXB0UHJlcHJvY2Vzc29yQ29udHJvbGxlcixcclxuICBvcmlnaW5hbFVzZXJQcm9tcHQ6IHN0cmluZyxcclxuICBmaWxlczogQXJyYXk8RmlsZUhhbmRsZT4sXHJcbik6IFByb21pc2U8c3RyaW5nPiB7XHJcbiAgY29uc3QgcGx1Z2luQ29uZmlnID0gY3RsLmdldFBsdWdpbkNvbmZpZyhjb25maWdTY2hlbWF0aWNzKTtcclxuICBjb25zdCByZXRyaWV2YWxMaW1pdCA9IHBsdWdpbkNvbmZpZy5nZXQoXCJyZXRyaWV2YWxMaW1pdFwiKTtcclxuICBjb25zdCByZXRyaWV2YWxBZmZpbml0eVRocmVzaG9sZCA9IHBsdWdpbkNvbmZpZy5nZXQoXCJyZXRyaWV2YWxBZmZpbml0eVRocmVzaG9sZFwiKTtcclxuXHJcbiAgLy8gcHJvY2VzcyBmaWxlcyBpZiBuZWNlc3NhcnlcclxuXHJcbiAgY29uc3Qgc3RhdHVzU3RlcHMgPSBuZXcgTWFwPEZpbGVIYW5kbGUsIFByZWRpY3Rpb25Qcm9jZXNzU3RhdHVzQ29udHJvbGxlcj4oKTtcclxuXHJcbiAgY29uc3QgcmV0cmlldmluZ1N0YXR1cyA9IGN0bC5jcmVhdGVTdGF0dXMoe1xyXG4gICAgc3RhdHVzOiBcImxvYWRpbmdcIixcclxuICAgIHRleHQ6IGBMb2FkaW5nIGFuIGVtYmVkZGluZyBtb2RlbCBmb3IgcmV0cmlldmFsLi4uYCxcclxuICB9KTtcclxuICBjb25zdCBtb2RlbCA9IGF3YWl0IGN0bC5jbGllbnQuZW1iZWRkaW5nLm1vZGVsKFwibm9taWMtYWkvbm9taWMtZW1iZWQtdGV4dC12MS41LUdHVUZcIiwge1xyXG4gICAgc2lnbmFsOiBjdGwuYWJvcnRTaWduYWwsXHJcbiAgfSk7XHJcbiAgcmV0cmlldmluZ1N0YXR1cy5zZXRTdGF0ZSh7XHJcbiAgICBzdGF0dXM6IFwibG9hZGluZ1wiLFxyXG4gICAgdGV4dDogYFJldHJpZXZpbmcgcmVsZXZhbnQgY2l0YXRpb25zIGZvciB1c2VyIHF1ZXJ5Li4uYCxcclxuICB9KTtcclxuICBjb25zdCByZXN1bHQgPSBhd2FpdCBjdGwuY2xpZW50LmZpbGVzLnJldHJpZXZlKG9yaWdpbmFsVXNlclByb21wdCwgZmlsZXMsIHtcclxuICAgIGVtYmVkZGluZ01vZGVsOiBtb2RlbCxcclxuICAgIC8vIEFmZmluaXR5IHRocmVzaG9sZDogMC42IG5vdCBpbXBsZW1lbnRlZFxyXG4gICAgbGltaXQ6IHJldHJpZXZhbExpbWl0LFxyXG4gICAgc2lnbmFsOiBjdGwuYWJvcnRTaWduYWwsXHJcbiAgICBvbkZpbGVQcm9jZXNzTGlzdChmaWxlc1RvUHJvY2Vzcykge1xyXG4gICAgICBmb3IgKGNvbnN0IGZpbGUgb2YgZmlsZXNUb1Byb2Nlc3MpIHtcclxuICAgICAgICBzdGF0dXNTdGVwcy5zZXQoXHJcbiAgICAgICAgICBmaWxlLFxyXG4gICAgICAgICAgcmV0cmlldmluZ1N0YXR1cy5hZGRTdWJTdGF0dXMoe1xyXG4gICAgICAgICAgICBzdGF0dXM6IFwid2FpdGluZ1wiLFxyXG4gICAgICAgICAgICB0ZXh0OiBgUHJvY2VzcyAke2ZpbGUubmFtZX0gZm9yIHJldHJpZXZhbGAsXHJcbiAgICAgICAgICB9KSxcclxuICAgICAgICApO1xyXG4gICAgICB9XHJcbiAgICB9LFxyXG4gICAgb25GaWxlUHJvY2Vzc2luZ1N0YXJ0KGZpbGUpIHtcclxuICAgICAgc3RhdHVzU3RlcHNcclxuICAgICAgICAuZ2V0KGZpbGUpIVxyXG4gICAgICAgIC5zZXRTdGF0ZSh7IHN0YXR1czogXCJsb2FkaW5nXCIsIHRleHQ6IGBQcm9jZXNzaW5nICR7ZmlsZS5uYW1lfSBmb3IgcmV0cmlldmFsYCB9KTtcclxuICAgIH0sXHJcbiAgICBvbkZpbGVQcm9jZXNzaW5nRW5kKGZpbGUpIHtcclxuICAgICAgc3RhdHVzU3RlcHNcclxuICAgICAgICAuZ2V0KGZpbGUpIVxyXG4gICAgICAgIC5zZXRTdGF0ZSh7IHN0YXR1czogXCJkb25lXCIsIHRleHQ6IGBQcm9jZXNzZWQgJHtmaWxlLm5hbWV9IGZvciByZXRyaWV2YWxgIH0pO1xyXG4gICAgfSxcclxuICAgIG9uRmlsZVByb2Nlc3NpbmdTdGVwUHJvZ3Jlc3MoZmlsZSwgc3RlcCwgcHJvZ3Jlc3NJblN0ZXApIHtcclxuICAgICAgY29uc3QgdmVyYiA9IHN0ZXAgPT09IFwibG9hZGluZ1wiID8gXCJMb2FkaW5nXCIgOiBzdGVwID09PSBcImNodW5raW5nXCIgPyBcIkNodW5raW5nXCIgOiBcIkVtYmVkZGluZ1wiO1xyXG4gICAgICBzdGF0dXNTdGVwcy5nZXQoZmlsZSkhLnNldFN0YXRlKHtcclxuICAgICAgICBzdGF0dXM6IFwibG9hZGluZ1wiLFxyXG4gICAgICAgIHRleHQ6IGAke3ZlcmJ9ICR7ZmlsZS5uYW1lfSBmb3IgcmV0cmlldmFsICgkeyhwcm9ncmVzc0luU3RlcCAqIDEwMCkudG9GaXhlZCgxKX0lKWAsXHJcbiAgICAgIH0pO1xyXG4gICAgfSxcclxuICB9KTtcclxuXHJcbiAgcmVzdWx0LmVudHJpZXMgPSByZXN1bHQuZW50cmllcy5maWx0ZXIoZW50cnkgPT4gZW50cnkuc2NvcmUgPiByZXRyaWV2YWxBZmZpbml0eVRocmVzaG9sZCk7XHJcblxyXG4gIC8vIGluamVjdCByZXRyaWV2YWwgcmVzdWx0IGludG8gdGhlIFwicHJvY2Vzc2VkXCIgY29udGVudFxyXG4gIGxldCBwcm9jZXNzZWRDb250ZW50ID0gXCJcIjtcclxuICBjb25zdCBudW1SZXRyaWV2YWxzID0gcmVzdWx0LmVudHJpZXMubGVuZ3RoO1xyXG4gIGlmIChudW1SZXRyaWV2YWxzID4gMCkge1xyXG4gICAgLy8gcmV0cmlldmFsIG9jY3VyZWQgYW5kIGdvdCByZXN1bHRzXHJcbiAgICAvLyBzaG93IHN0YXR1c1xyXG4gICAgcmV0cmlldmluZ1N0YXR1cy5zZXRTdGF0ZSh7XHJcbiAgICAgIHN0YXR1czogXCJkb25lXCIsXHJcbiAgICAgIHRleHQ6IGBSZXRyaWV2ZWQgJHtudW1SZXRyaWV2YWxzfSByZWxldmFudCBjaXRhdGlvbnMgZm9yIHVzZXIgcXVlcnlgLFxyXG4gICAgfSk7XHJcbiAgICBjdGwuZGVidWcoXCJSZXRyaWV2YWwgcmVzdWx0c1wiLCByZXN1bHQpO1xyXG4gICAgLy8gYWRkIHJlc3VsdHMgdG8gcHJvbXB0XHJcbiAgICBjb25zdCBwcmVmaXggPSBcIlRoZSBmb2xsb3dpbmcgY2l0YXRpb25zIHdlcmUgZm91bmQgaW4gdGhlIGZpbGVzIHByb3ZpZGVkIGJ5IHRoZSB1c2VyOlxcblxcblwiO1xyXG4gICAgcHJvY2Vzc2VkQ29udGVudCArPSBwcmVmaXg7XHJcbiAgICBsZXQgY2l0YXRpb25OdW1iZXIgPSAxO1xyXG4gICAgcmVzdWx0LmVudHJpZXMuZm9yRWFjaChyZXN1bHQgPT4ge1xyXG4gICAgICBjb25zdCBjb21wbGV0ZVRleHQgPSByZXN1bHQuY29udGVudDtcclxuICAgICAgcHJvY2Vzc2VkQ29udGVudCArPSBgQ2l0YXRpb24gJHtjaXRhdGlvbk51bWJlcn06IFwiJHtjb21wbGV0ZVRleHR9XCJcXG5cXG5gO1xyXG4gICAgICBjaXRhdGlvbk51bWJlcisrO1xyXG4gICAgfSk7XHJcbiAgICBhd2FpdCBjdGwuYWRkQ2l0YXRpb25zKHJlc3VsdCk7XHJcbiAgICBjb25zdCBzdWZmaXggPVxyXG4gICAgICBgVXNlIHRoZSBjaXRhdGlvbnMgYWJvdmUgdG8gcmVzcG9uZCB0byB0aGUgdXNlciBxdWVyeSwgb25seSBpZiB0aGV5IGFyZSByZWxldmFudC4gYCArXHJcbiAgICAgIGBPdGhlcndpc2UsIHJlc3BvbmQgdG8gdGhlIGJlc3Qgb2YgeW91ciBhYmlsaXR5IHdpdGhvdXQgdGhlbS5gICtcclxuICAgICAgYFxcblxcblVzZXIgUXVlcnk6XFxuXFxuJHtvcmlnaW5hbFVzZXJQcm9tcHR9YDtcclxuICAgIHByb2Nlc3NlZENvbnRlbnQgKz0gc3VmZml4O1xyXG4gIH0gZWxzZSB7XHJcbiAgICAvLyByZXRyaWV2YWwgb2NjdXJlZCBidXQgbm8gcmVsZXZhbnQgY2l0YXRpb25zIGZvdW5kXHJcbiAgICByZXRyaWV2aW5nU3RhdHVzLnNldFN0YXRlKHtcclxuICAgICAgc3RhdHVzOiBcImNhbmNlbGVkXCIsXHJcbiAgICAgIHRleHQ6IGBObyByZWxldmFudCBjaXRhdGlvbnMgZm91bmQgZm9yIHVzZXIgcXVlcnlgLFxyXG4gICAgfSk7XHJcbiAgICBjdGwuZGVidWcoXCJObyByZWxldmFudCBjaXRhdGlvbnMgZm91bmQgZm9yIHVzZXIgcXVlcnlcIik7XHJcbiAgICBjb25zdCBub3RlQWJvdXROb1JldHJpZXZhbFJlc3VsdHNGb3VuZCA9XHJcbiAgICAgIGBJbXBvcnRhbnQ6IE5vIGNpdGF0aW9ucyB3ZXJlIGZvdW5kIGluIHRoZSB1c2VyIGZpbGVzIGZvciB0aGUgdXNlciBxdWVyeS4gYCArXHJcbiAgICAgIGBJbiBsZXNzIHRoYW4gb25lIHNlbnRlbmNlLCBpbmZvcm0gdGhlIHVzZXIgb2YgdGhpcy4gYCArXHJcbiAgICAgIGBUaGVuIHJlc3BvbmQgdG8gdGhlIHF1ZXJ5IHRvIHRoZSBiZXN0IG9mIHlvdXIgYWJpbGl0eS5gO1xyXG4gICAgcHJvY2Vzc2VkQ29udGVudCA9XHJcbiAgICAgIG5vdGVBYm91dE5vUmV0cmlldmFsUmVzdWx0c0ZvdW5kICsgYFxcblxcblVzZXIgUXVlcnk6XFxuXFxuJHtvcmlnaW5hbFVzZXJQcm9tcHR9YDtcclxuICB9XHJcbiAgY3RsLmRlYnVnKFwiUHJvY2Vzc2VkIGNvbnRlbnRcIiwgcHJvY2Vzc2VkQ29udGVudCk7XHJcblxyXG4gIHJldHVybiBwcm9jZXNzZWRDb250ZW50O1xyXG59XHJcblxyXG5hc3luYyBmdW5jdGlvbiBwcmVwYXJlRG9jdW1lbnRDb250ZXh0SW5qZWN0aW9uKFxyXG4gIGN0bDogUHJvbXB0UHJlcHJvY2Vzc29yQ29udHJvbGxlcixcclxuICBpbnB1dDogQ2hhdE1lc3NhZ2UsXHJcbik6IFByb21pc2U8Q2hhdE1lc3NhZ2U+IHtcclxuICBjb25zdCBkb2N1bWVudEluamVjdGlvblNuaXBwZXRzOiBNYXA8RmlsZUhhbmRsZSwgc3RyaW5nPiA9IG5ldyBNYXAoKTtcclxuICBjb25zdCBmaWxlcyA9IGlucHV0LmNvbnN1bWVGaWxlcyhjdGwuY2xpZW50LCBmaWxlID0+IGZpbGUudHlwZSAhPT0gXCJpbWFnZVwiKTtcclxuICBmb3IgKGNvbnN0IGZpbGUgb2YgZmlsZXMpIHtcclxuICAgIC8vIFRoaXMgc2hvdWxkIHRha2Ugbm8gdGltZSBhcyB0aGUgcmVzdWx0IGlzIGFscmVhZHkgaW4gdGhlIGNhY2hlXHJcbiAgICBjb25zdCB7IGNvbnRlbnQgfSA9IGF3YWl0IGN0bC5jbGllbnQuZmlsZXMucGFyc2VEb2N1bWVudChmaWxlLCB7XHJcbiAgICAgIHNpZ25hbDogY3RsLmFib3J0U2lnbmFsLFxyXG4gICAgfSk7XHJcblxyXG4gICAgY3RsLmRlYnVnKHRleHRgXHJcbiAgICAgIFN0cmF0ZWd5OiBpbmplY3QtZnVsbC1jb250ZW50LiBJbmplY3RpbmcgZnVsbCBjb250ZW50IG9mIGZpbGUgJyR7ZmlsZX0nIGludG8gdGhlXHJcbiAgICAgIGNvbnRleHQuIExlbmd0aDogJHtjb250ZW50Lmxlbmd0aH0uXHJcbiAgICBgKTtcclxuICAgIGRvY3VtZW50SW5qZWN0aW9uU25pcHBldHMuc2V0KGZpbGUsIGNvbnRlbnQpO1xyXG4gIH1cclxuXHJcbiAgLy8gRm9ybWF0IHRoZSBmaW5hbCB1c2VyIHByb21wdFxyXG4gIC8vIFRPRE86XHJcbiAgLy8gICAgTWFrZSB0aGlzIHRlbXBsYXRhYmxlIGFuZCBjb25maWd1cmFibGVcclxuICAvLyAgICAgIGh0dHBzOi8vZ2l0aHViLmNvbS9sbXN0dWRpby1haS9sbG1zdGVyL2lzc3Vlcy8xMDE3XHJcbiAgbGV0IGZvcm1hdHRlZEZpbmFsVXNlclByb21wdCA9IFwiXCI7XHJcblxyXG4gIGlmIChkb2N1bWVudEluamVjdGlvblNuaXBwZXRzLnNpemUgPiAwKSB7XHJcbiAgICBmb3JtYXR0ZWRGaW5hbFVzZXJQcm9tcHQgKz1cclxuICAgICAgXCJUaGlzIGlzIGEgRW5yaWNoZWQgQ29udGV4dCBHZW5lcmF0aW9uIHNjZW5hcmlvLlxcblxcblRoZSBmb2xsb3dpbmcgY29udGVudCB3YXMgZm91bmQgaW4gdGhlIGZpbGVzIHByb3ZpZGVkIGJ5IHRoZSB1c2VyLlxcblwiO1xyXG5cclxuICAgIGZvciAoY29uc3QgW2ZpbGVIYW5kbGUsIHNuaXBwZXRdIG9mIGRvY3VtZW50SW5qZWN0aW9uU25pcHBldHMpIHtcclxuICAgICAgZm9ybWF0dGVkRmluYWxVc2VyUHJvbXB0ICs9IGBcXG5cXG4qKiAke2ZpbGVIYW5kbGUubmFtZX0gZnVsbCBjb250ZW50ICoqXFxuXFxuJHtzbmlwcGV0fVxcblxcbioqIGVuZCBvZiAke2ZpbGVIYW5kbGUubmFtZX0gKipcXG5cXG5gO1xyXG4gICAgfVxyXG5cclxuICAgIGZvcm1hdHRlZEZpbmFsVXNlclByb21wdCArPSBgQmFzZWQgb24gdGhlIGNvbnRlbnQgYWJvdmUsIHBsZWFzZSBwcm92aWRlIGEgcmVzcG9uc2UgdG8gdGhlIHVzZXIgcXVlcnkuXFxuXFxuVXNlciBxdWVyeTogJHtpbnB1dC5nZXRUZXh0KCl9YDtcclxuICB9XHJcblxyXG4gIGlucHV0LnJlcGxhY2VUZXh0KGZvcm1hdHRlZEZpbmFsVXNlclByb21wdCk7XHJcbiAgcmV0dXJuIGlucHV0O1xyXG59XHJcblxyXG5hc3luYyBmdW5jdGlvbiBnZXRFZmZlY3RpdmVDb250ZXh0Rm9ybWF0dGVkKFxyXG4gIGN0eDogQ2hhdCxcclxuICBtb2RlbDogTExNRHluYW1pY0hhbmRsZSxcclxuICBjdGw6IFByb21wdFByZXByb2Nlc3NvckNvbnRyb2xsZXIsXHJcbikge1xyXG4gIHRyeSB7XHJcbiAgICByZXR1cm4gYXdhaXQgbW9kZWwuYXBwbHlQcm9tcHRUZW1wbGF0ZShjdHgpO1xyXG4gIH0gY2F0Y2ggKGUpIHtcclxuICAgIGNvbnN0IGhhc0FueVVzZXJNZXNzYWdlID0gY3R4LmdldE1lc3NhZ2VzQXJyYXkoKS5zb21lKG1lc3NhZ2UgPT4gbWVzc2FnZS5nZXRSb2xlKCkgPT09IFwidXNlclwiKTtcclxuICAgIGlmICghaGFzQW55VXNlck1lc3NhZ2UpIHtcclxuICAgICAgLy8gU29tZSBwcm9tcHQgdGVtcGxhdGVzIHRocm93IG9uIG5vIHVzZXIgbWVzc2FnZS4gQWRkIGEgbWluaW1hbCBwbGFjZWhvbGRlciBhbmQgdHJ5IGFnYWluXHJcbiAgICAgIGNvbnN0IHBsYWNlaG9sZGVyVXNlck1lc3NhZ2VDb250ZW50ID0gXCI/XCI7IC8vIG5vbi13aGl0ZXNwYWNlIHRvIGF2b2lkIHRlbXBsYXRlIHRyaW1taW5nXHJcbiAgICAgIGN0bC5kZWJ1Zyh0ZXh0YFxyXG4gICAgICAgIEZhaWxlZCB0byBhcHBseSBwcm9tcHQgdGVtcGxhdGUgb24gY29udGV4dCB3aXRoIG5vIHVzZXIgbWVzc2FnZXMuIFJldHJ5aW5nIHdpdGggcGxhY2Vob2xkZXJcclxuICAgICAgICB1c2VyIG1lc3NhZ2UuXHJcbiAgICAgIGApO1xyXG4gICAgICBjb25zdCBtZWFzdXJlbWVudENvbnRleHQgPSBjdHgud2l0aEFwcGVuZGVkKFwidXNlclwiLCBwbGFjZWhvbGRlclVzZXJNZXNzYWdlQ29udGVudCk7XHJcbiAgICAgIHJldHVybiBhd2FpdCBtb2RlbC5hcHBseVByb21wdFRlbXBsYXRlKG1lYXN1cmVtZW50Q29udGV4dCk7XHJcbiAgICB9XHJcbiAgICB0aHJvdyBlO1xyXG4gIH1cclxufVxyXG5cclxuYXN5bmMgZnVuY3Rpb24gbWVhc3VyZUNvbnRleHRXaW5kb3coXHJcbiAgY3R4OiBDaGF0LFxyXG4gIG1vZGVsOiBMTE1EeW5hbWljSGFuZGxlLFxyXG4gIGN0bDogUHJvbXB0UHJlcHJvY2Vzc29yQ29udHJvbGxlcixcclxuKSB7XHJcbiAgY29uc3QgY3VycmVudENvbnRleHRGb3JtYXR0ZWQgPSBhd2FpdCBnZXRFZmZlY3RpdmVDb250ZXh0Rm9ybWF0dGVkKGN0eCwgbW9kZWwsIGN0bCk7XHJcbiAgY29uc3QgdG90YWxUb2tlbnNJbkNvbnRleHQgPSBhd2FpdCBtb2RlbC5jb3VudFRva2VucyhjdXJyZW50Q29udGV4dEZvcm1hdHRlZCk7XHJcbiAgY29uc3QgbW9kZWxDb250ZXh0TGVuZ3RoID0gYXdhaXQgbW9kZWwuZ2V0Q29udGV4dExlbmd0aCgpO1xyXG4gIGNvbnN0IG1vZGVsUmVtYWluaW5nQ29udGV4dExlbmd0aCA9IG1vZGVsQ29udGV4dExlbmd0aCAtIHRvdGFsVG9rZW5zSW5Db250ZXh0O1xyXG4gIGNvbnN0IGNvbnRleHRPY2N1cGllZFBlcmNlbnQgPSAodG90YWxUb2tlbnNJbkNvbnRleHQgLyBtb2RlbENvbnRleHRMZW5ndGgpICogMTAwO1xyXG4gIHJldHVybiB7XHJcbiAgICB0b3RhbFRva2Vuc0luQ29udGV4dCxcclxuICAgIG1vZGVsQ29udGV4dExlbmd0aCxcclxuICAgIG1vZGVsUmVtYWluaW5nQ29udGV4dExlbmd0aCxcclxuICAgIGNvbnRleHRPY2N1cGllZFBlcmNlbnQsXHJcbiAgfTtcclxufVxyXG5cclxuYXN5bmMgZnVuY3Rpb24gY2hvb3NlQ29udGV4dEluamVjdGlvblN0cmF0ZWd5KFxyXG4gIGN0bDogUHJvbXB0UHJlcHJvY2Vzc29yQ29udHJvbGxlcixcclxuICBvcmlnaW5hbFVzZXJQcm9tcHQ6IHN0cmluZyxcclxuICBmaWxlczogQXJyYXk8RmlsZUhhbmRsZT4sXHJcbik6IFByb21pc2U8RG9jdW1lbnRDb250ZXh0SW5qZWN0aW9uU3RyYXRlZ3k+IHtcclxuICBjb25zdCBzdGF0dXMgPSBjdGwuY3JlYXRlU3RhdHVzKHtcclxuICAgIHN0YXR1czogXCJsb2FkaW5nXCIsXHJcbiAgICB0ZXh0OiBgRGVjaWRpbmcgaG93IHRvIGhhbmRsZSB0aGUgZG9jdW1lbnQocykuLi5gLFxyXG4gIH0pO1xyXG5cclxuICBjb25zdCBtb2RlbCA9IGF3YWl0IGN0bC5jbGllbnQubGxtLm1vZGVsKCk7XHJcbiAgY29uc3QgY3R4ID0gYXdhaXQgY3RsLnB1bGxIaXN0b3J5KCk7XHJcblxyXG4gIC8vIE1lYXN1cmUgdGhlIGNvbnRleHQgd2luZG93XHJcbiAgY29uc3Qge1xyXG4gICAgdG90YWxUb2tlbnNJbkNvbnRleHQsXHJcbiAgICBtb2RlbENvbnRleHRMZW5ndGgsXHJcbiAgICBtb2RlbFJlbWFpbmluZ0NvbnRleHRMZW5ndGgsXHJcbiAgICBjb250ZXh0T2NjdXBpZWRQZXJjZW50LFxyXG4gIH0gPSBhd2FpdCBtZWFzdXJlQ29udGV4dFdpbmRvdyhjdHgsIG1vZGVsLCBjdGwpO1xyXG5cclxuICBjdGwuZGVidWcoXHJcbiAgICBgQ29udGV4dCBtZWFzdXJlbWVudCByZXN1bHQ6XFxuXFxuYCArXHJcbiAgICAgIGBcXHRUb3RhbCB0b2tlbnMgaW4gY29udGV4dDogJHt0b3RhbFRva2Vuc0luQ29udGV4dH1cXG5gICtcclxuICAgICAgYFxcdE1vZGVsIGNvbnRleHQgbGVuZ3RoOiAke21vZGVsQ29udGV4dExlbmd0aH1cXG5gICtcclxuICAgICAgYFxcdE1vZGVsIHJlbWFpbmluZyBjb250ZXh0IGxlbmd0aDogJHttb2RlbFJlbWFpbmluZ0NvbnRleHRMZW5ndGh9XFxuYCArXHJcbiAgICAgIGBcXHRDb250ZXh0IG9jY3VwaWVkIHBlcmNlbnQ6ICR7Y29udGV4dE9jY3VwaWVkUGVyY2VudC50b0ZpeGVkKDIpfSVcXG5gLFxyXG4gICk7XHJcblxyXG4gIC8vIEdldCB0b2tlbiBjb3VudCBvZiBwcm92aWRlZCBmaWxlc1xyXG4gIGxldCB0b3RhbEZpbGVUb2tlbkNvdW50ID0gMDtcclxuICBsZXQgdG90YWxSZWFkVGltZSA9IDA7XHJcbiAgbGV0IHRvdGFsVG9rZW5pemVUaW1lID0gMDtcclxuICBmb3IgKGNvbnN0IGZpbGUgb2YgZmlsZXMpIHtcclxuICAgIGNvbnN0IHN0YXJ0VGltZSA9IHBlcmZvcm1hbmNlLm5vdygpO1xyXG5cclxuICAgIGNvbnN0IGxvYWRpbmdTdGF0dXMgPSBzdGF0dXMuYWRkU3ViU3RhdHVzKHtcclxuICAgICAgc3RhdHVzOiBcImxvYWRpbmdcIixcclxuICAgICAgdGV4dDogYExvYWRpbmcgcGFyc2VyIGZvciAke2ZpbGUubmFtZX0uLi5gLFxyXG4gICAgfSk7XHJcbiAgICBsZXQgYWN0aW9uUHJvZ3Jlc3NpbmcgPSBcIlJlYWRpbmdcIjtcclxuICAgIGxldCBwYXJzZXJJbmRpY2F0b3IgPSBcIlwiO1xyXG5cclxuICAgIGNvbnN0IHsgY29udGVudCB9ID0gYXdhaXQgY3RsLmNsaWVudC5maWxlcy5wYXJzZURvY3VtZW50KGZpbGUsIHtcclxuICAgICAgc2lnbmFsOiBjdGwuYWJvcnRTaWduYWwsXHJcbiAgICAgIG9uUGFyc2VyTG9hZGVkOiBwYXJzZXIgPT4ge1xyXG4gICAgICAgIGxvYWRpbmdTdGF0dXMuc2V0U3RhdGUoe1xyXG4gICAgICAgICAgc3RhdHVzOiBcImxvYWRpbmdcIixcclxuICAgICAgICAgIHRleHQ6IGAke3BhcnNlci5saWJyYXJ5fSBsb2FkZWQgZm9yICR7ZmlsZS5uYW1lfS4uLmAsXHJcbiAgICAgICAgfSk7XHJcbiAgICAgICAgLy8gVXBkYXRlIGFjdGlvbiBuYW1lcyBpZiB3ZSdyZSB1c2luZyBhIHBhcnNpbmcgZnJhbWV3b3JrXHJcbiAgICAgICAgaWYgKHBhcnNlci5saWJyYXJ5ICE9PSBcImJ1aWx0SW5cIikge1xyXG4gICAgICAgICAgYWN0aW9uUHJvZ3Jlc3NpbmcgPSBcIlBhcnNpbmdcIjtcclxuICAgICAgICAgIHBhcnNlckluZGljYXRvciA9IGAgd2l0aCAke3BhcnNlci5saWJyYXJ5fWA7XHJcbiAgICAgICAgfVxyXG4gICAgICB9LFxyXG4gICAgICBvblByb2dyZXNzOiBwcm9ncmVzcyA9PiB7XHJcbiAgICAgICAgbG9hZGluZ1N0YXR1cy5zZXRTdGF0ZSh7XHJcbiAgICAgICAgICBzdGF0dXM6IFwibG9hZGluZ1wiLFxyXG4gICAgICAgICAgdGV4dDogYCR7YWN0aW9uUHJvZ3Jlc3Npbmd9IGZpbGUgJHtmaWxlLm5hbWV9JHtwYXJzZXJJbmRpY2F0b3J9Li4uICgkeyhcclxuICAgICAgICAgICAgcHJvZ3Jlc3MgKiAxMDBcclxuICAgICAgICAgICkudG9GaXhlZCgyKX0lKWAsXHJcbiAgICAgICAgfSk7XHJcbiAgICAgIH0sXHJcbiAgICB9KTtcclxuICAgIGxvYWRpbmdTdGF0dXMucmVtb3ZlKCk7XHJcblxyXG4gICAgdG90YWxSZWFkVGltZSArPSBwZXJmb3JtYW5jZS5ub3coKSAtIHN0YXJ0VGltZTtcclxuXHJcbiAgICAvLyB0b2tlbml6ZSBmaWxlIGNvbnRlbnRcclxuICAgIGNvbnN0IHN0YXJ0VG9rZW5pemVUaW1lID0gcGVyZm9ybWFuY2Uubm93KCk7XHJcbiAgICB0b3RhbEZpbGVUb2tlbkNvdW50ICs9IGF3YWl0IG1vZGVsLmNvdW50VG9rZW5zKGNvbnRlbnQpO1xyXG4gICAgdG90YWxUb2tlbml6ZVRpbWUgKz0gcGVyZm9ybWFuY2Uubm93KCkgLSBzdGFydFRva2VuaXplVGltZTtcclxuICAgIGlmICh0b3RhbEZpbGVUb2tlbkNvdW50ID4gbW9kZWxSZW1haW5pbmdDb250ZXh0TGVuZ3RoKSB7XHJcbiAgICAgIC8vIEVhcmx5IGV4aXQgaWYgd2UgYWxyZWFkeSBoYXZlIHRvbyBtdWNoIHRva2Vucy4gSGVscHMgd2l0aCBwZXJmb3JtYW5jZSB3aGVuIHRoZXJlIGFyZSBhIGxvdCBvZiBmaWxlcy5cclxuICAgICAgYnJlYWs7XHJcbiAgICB9XHJcbiAgfVxyXG4gIGN0bC5kZWJ1ZyhgVG90YWwgZmlsZSByZWFkIHRpbWU6ICR7dG90YWxSZWFkVGltZS50b0ZpeGVkKDIpfSBtc2ApO1xyXG4gIGN0bC5kZWJ1ZyhgVG90YWwgdG9rZW5pemUgdGltZTogJHt0b3RhbFRva2VuaXplVGltZS50b0ZpeGVkKDIpfSBtc2ApO1xyXG5cclxuICAvLyBDYWxjdWxhdGUgdG90YWwgdG9rZW4gY291bnQgb2YgZmlsZXMgKyB1c2VyIHByb21wdFxyXG4gIGN0bC5kZWJ1ZyhgT3JpZ2luYWwgVXNlciBQcm9tcHQ6ICR7b3JpZ2luYWxVc2VyUHJvbXB0fWApO1xyXG4gIGNvbnN0IHVzZXJQcm9tcHRUb2tlbkNvdW50ID0gKGF3YWl0IG1vZGVsLnRva2VuaXplKG9yaWdpbmFsVXNlclByb21wdCkpLmxlbmd0aDtcclxuICBjb25zdCB0b3RhbEZpbGVQbHVzUHJvbXB0VG9rZW5Db3VudCA9IHRvdGFsRmlsZVRva2VuQ291bnQgKyB1c2VyUHJvbXB0VG9rZW5Db3VudDtcclxuXHJcbiAgLy8gQ2FsY3VsYXRlIHRoZSBhdmFpbGFibGUgY29udGV4dCB0b2tlbnNcclxuICBjb25zdCBjb250ZXh0T2NjdXBpZWRGcmFjdGlvbiA9IGNvbnRleHRPY2N1cGllZFBlcmNlbnQgLyAxMDA7XHJcbiAgY29uc3QgdGFyZ2V0Q29udGV4dFVzZVBlcmNlbnQgPSAwLjc7XHJcbiAgY29uc3QgdGFyZ2V0Q29udGV4dFVzYWdlID0gdGFyZ2V0Q29udGV4dFVzZVBlcmNlbnQgKiAoMSAtIGNvbnRleHRPY2N1cGllZEZyYWN0aW9uKTtcclxuICBjb25zdCBhdmFpbGFibGVDb250ZXh0VG9rZW5zID0gTWF0aC5mbG9vcihtb2RlbFJlbWFpbmluZ0NvbnRleHRMZW5ndGggKiB0YXJnZXRDb250ZXh0VXNhZ2UpO1xyXG5cclxuICAvLyBEZWJ1ZyBsb2dcclxuICBjdGwuZGVidWcoXCJTdHJhdGVneSBDYWxjdWxhdGlvbjpcIik7XHJcbiAgY3RsLmRlYnVnKGBcXHRUb3RhbCBUb2tlbnMgaW4gQWxsIEZpbGVzOiAke3RvdGFsRmlsZVRva2VuQ291bnR9YCk7XHJcbiAgY3RsLmRlYnVnKGBcXHRUb3RhbCBUb2tlbnMgaW4gVXNlciBQcm9tcHQ6ICR7dXNlclByb21wdFRva2VuQ291bnR9YCk7XHJcbiAgY3RsLmRlYnVnKGBcXHRNb2RlbCBDb250ZXh0IFJlbWFpbmluZzogJHttb2RlbFJlbWFpbmluZ0NvbnRleHRMZW5ndGh9IHRva2Vuc2ApO1xyXG4gIGN0bC5kZWJ1ZyhgXFx0Q29udGV4dCBPY2N1cGllZDogJHtjb250ZXh0T2NjdXBpZWRQZXJjZW50LnRvRml4ZWQoMil9JWApO1xyXG4gIGN0bC5kZWJ1ZyhgXFx0QXZhaWxhYmxlIFRva2VuczogJHthdmFpbGFibGVDb250ZXh0VG9rZW5zfVxcbmApO1xyXG5cclxuICBpZiAodG90YWxGaWxlUGx1c1Byb21wdFRva2VuQ291bnQgPiBhdmFpbGFibGVDb250ZXh0VG9rZW5zKSB7XHJcbiAgICBjb25zdCBjaG9zZW5TdHJhdGVneSA9IFwicmV0cmlldmFsXCI7XHJcbiAgICBjdGwuZGVidWcoXHJcbiAgICAgIGBDaG9zZW4gY29udGV4dCBpbmplY3Rpb24gc3RyYXRlZ3k6ICcke2Nob3NlblN0cmF0ZWd5fScuIFRvdGFsIGZpbGUgKyBwcm9tcHQgdG9rZW4gY291bnQ6IGAgK1xyXG4gICAgICAgIGAke3RvdGFsRmlsZVBsdXNQcm9tcHRUb2tlbkNvdW50fSA+ICR7XHJcbiAgICAgICAgICB0YXJnZXRDb250ZXh0VXNhZ2UgKiAxMDBcclxuICAgICAgICB9JSAqIGF2YWlsYWJsZSBjb250ZXh0IHRva2VuczogJHthdmFpbGFibGVDb250ZXh0VG9rZW5zfWAsXHJcbiAgICApO1xyXG4gICAgc3RhdHVzLnNldFN0YXRlKHtcclxuICAgICAgc3RhdHVzOiBcImRvbmVcIixcclxuICAgICAgdGV4dDogYENob3NlbiBjb250ZXh0IGluamVjdGlvbiBzdHJhdGVneTogJyR7Y2hvc2VuU3RyYXRlZ3l9Jy4gUmV0cmlldmFsIGlzIG9wdGltYWwgZm9yIHRoZSBzaXplIG9mIGNvbnRlbnQgcHJvdmlkZWRgLFxyXG4gICAgfSk7XHJcbiAgICByZXR1cm4gY2hvc2VuU3RyYXRlZ3k7XHJcbiAgfVxyXG5cclxuICAvLyBUT0RPOlxyXG4gIC8vXHJcbiAgLy8gICBDb25zaWRlciBhIG1vcmUgc29waGlzdGljYXRlZCBzdHJhdGVneSB3aGVyZSB3ZSBpbmplY3Qgc29tZSBoZWFkZXIgb3Igc3VtbWFyeSBjb250ZW50XHJcbiAgLy8gICBhbmQgdGhlbiBwZXJmb3JtIHJldHJpZXZhbCBvbiB0aGUgcmVzdCBvZiB0aGUgY29udGVudC5cclxuICAvL1xyXG4gIC8vXHJcblxyXG4gIGNvbnN0IGNob3NlblN0cmF0ZWd5ID0gXCJpbmplY3QtZnVsbC1jb250ZW50XCI7XHJcbiAgc3RhdHVzLnNldFN0YXRlKHtcclxuICAgIHN0YXR1czogXCJkb25lXCIsXHJcbiAgICB0ZXh0OiBgQ2hvc2VuIGNvbnRleHQgaW5qZWN0aW9uIHN0cmF0ZWd5OiAnJHtjaG9zZW5TdHJhdGVneX0nLiBBbGwgY29udGVudCBjYW4gZml0IGludG8gdGhlIGNvbnRleHRgLFxyXG4gIH0pO1xyXG4gIHJldHVybiBjaG9zZW5TdHJhdGVneTtcclxufVxyXG4iLCAiaW1wb3J0IHsgdHlwZSBQbHVnaW5Db250ZXh0IH0gZnJvbSBcIkBsbXN0dWRpby9zZGtcIjtcclxuaW1wb3J0IHsgY29uZmlnU2NoZW1hdGljcyB9IGZyb20gXCIuL2NvbmZpZ1wiO1xyXG5pbXBvcnQgeyBwcmVwcm9jZXNzIH0gZnJvbSBcIi4vcHJvbXB0UHJlcHJvY2Vzc29yXCI7XHJcblxyXG4vLyBUaGlzIGlzIHRoZSBlbnRyeSBwb2ludCBvZiB0aGUgcGx1Z2luLiBUaGUgbWFpbiBmdW5jdGlvbiBpcyB0byByZWdpc3RlciBkaWZmZXJlbnQgY29tcG9uZW50cyBvZlxyXG4vLyB0aGUgcGx1Z2luLCBzdWNoIGFzIHByb21wdFByZXByb2Nlc3NvciwgcHJlZGljdGlvbkxvb3BIYW5kbGVyLCBldGMuXHJcbi8vXHJcbi8vIFlvdSBkbyBub3QgbmVlZCB0byBtb2RpZnkgdGhpcyBmaWxlIHVubGVzcyB5b3Ugd2FudCB0byBhZGQgbW9yZSBjb21wb25lbnRzIHRvIHRoZSBwbHVnaW4sIGFuZC9vclxyXG4vLyBhZGQgY3VzdG9tIGluaXRpYWxpemF0aW9uIGxvZ2ljLlxyXG5cclxuZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIG1haW4oY29udGV4dDogUGx1Z2luQ29udGV4dCkge1xyXG4gIC8vIFJlZ2lzdGVyIHRoZSBjb25maWd1cmF0aW9uIHNjaGVtYXRpY3MuXHJcbiAgY29udGV4dC53aXRoQ29uZmlnU2NoZW1hdGljcyhjb25maWdTY2hlbWF0aWNzKTtcclxuICAvLyBSZWdpc3RlciB0aGUgcHJvbXB0UHJlcHJvY2Vzc29yLlxyXG4gIGNvbnRleHQud2l0aFByb21wdFByZXByb2Nlc3NvcihwcmVwcm9jZXNzKTtcclxufVxyXG4iLCAiaW1wb3J0IHsgTE1TdHVkaW9DbGllbnQsIHR5cGUgUGx1Z2luQ29udGV4dCB9IGZyb20gXCJAbG1zdHVkaW8vc2RrXCI7XG5cbmRlY2xhcmUgdmFyIHByb2Nlc3M6IGFueTtcblxuLy8gV2UgcmVjZWl2ZSBydW50aW1lIGluZm9ybWF0aW9uIGluIHRoZSBlbnZpcm9ubWVudCB2YXJpYWJsZXMuXG5jb25zdCBjbGllbnRJZGVudGlmaWVyID0gcHJvY2Vzcy5lbnYuTE1TX1BMVUdJTl9DTElFTlRfSURFTlRJRklFUjtcbmNvbnN0IGNsaWVudFBhc3NrZXkgPSBwcm9jZXNzLmVudi5MTVNfUExVR0lOX0NMSUVOVF9QQVNTS0VZO1xuY29uc3QgYmFzZVVybCA9IHByb2Nlc3MuZW52LkxNU19QTFVHSU5fQkFTRV9VUkw7XG5cbmNvbnN0IGNsaWVudCA9IG5ldyBMTVN0dWRpb0NsaWVudCh7XG4gIGNsaWVudElkZW50aWZpZXIsXG4gIGNsaWVudFBhc3NrZXksXG4gIGJhc2VVcmwsXG59KTtcblxuKGdsb2JhbFRoaXMgYXMgYW55KS5fX0xNU19QTFVHSU5fQ09OVEVYVCA9IHRydWU7XG5cbmxldCBwcmVkaWN0aW9uTG9vcEhhbmRsZXJTZXQgPSBmYWxzZTtcbmxldCBwcm9tcHRQcmVwcm9jZXNzb3JTZXQgPSBmYWxzZTtcbmxldCBjb25maWdTY2hlbWF0aWNzU2V0ID0gZmFsc2U7XG5sZXQgZ2xvYmFsQ29uZmlnU2NoZW1hdGljc1NldCA9IGZhbHNlO1xubGV0IHRvb2xzUHJvdmlkZXJTZXQgPSBmYWxzZTtcbmxldCBnZW5lcmF0b3JTZXQgPSBmYWxzZTtcblxuY29uc3Qgc2VsZlJlZ2lzdHJhdGlvbkhvc3QgPSBjbGllbnQucGx1Z2lucy5nZXRTZWxmUmVnaXN0cmF0aW9uSG9zdCgpO1xuXG5jb25zdCBwbHVnaW5Db250ZXh0OiBQbHVnaW5Db250ZXh0ID0ge1xuICB3aXRoUHJlZGljdGlvbkxvb3BIYW5kbGVyOiAoZ2VuZXJhdGUpID0+IHtcbiAgICBpZiAocHJlZGljdGlvbkxvb3BIYW5kbGVyU2V0KSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoXCJQcmVkaWN0aW9uTG9vcEhhbmRsZXIgYWxyZWFkeSByZWdpc3RlcmVkXCIpO1xuICAgIH1cbiAgICBpZiAodG9vbHNQcm92aWRlclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiUHJlZGljdGlvbkxvb3BIYW5kbGVyIGNhbm5vdCBiZSB1c2VkIHdpdGggYSB0b29scyBwcm92aWRlclwiKTtcbiAgICB9XG5cbiAgICBwcmVkaWN0aW9uTG9vcEhhbmRsZXJTZXQgPSB0cnVlO1xuICAgIHNlbGZSZWdpc3RyYXRpb25Ib3N0LnNldFByZWRpY3Rpb25Mb29wSGFuZGxlcihnZW5lcmF0ZSk7XG4gICAgcmV0dXJuIHBsdWdpbkNvbnRleHQ7XG4gIH0sXG4gIHdpdGhQcm9tcHRQcmVwcm9jZXNzb3I6IChwcmVwcm9jZXNzKSA9PiB7XG4gICAgaWYgKHByb21wdFByZXByb2Nlc3NvclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiUHJvbXB0UHJlcHJvY2Vzc29yIGFscmVhZHkgcmVnaXN0ZXJlZFwiKTtcbiAgICB9XG4gICAgcHJvbXB0UHJlcHJvY2Vzc29yU2V0ID0gdHJ1ZTtcbiAgICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5zZXRQcm9tcHRQcmVwcm9jZXNzb3IocHJlcHJvY2Vzcyk7XG4gICAgcmV0dXJuIHBsdWdpbkNvbnRleHQ7XG4gIH0sXG4gIHdpdGhDb25maWdTY2hlbWF0aWNzOiAoY29uZmlnU2NoZW1hdGljcykgPT4ge1xuICAgIGlmIChjb25maWdTY2hlbWF0aWNzU2V0KSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoXCJDb25maWcgc2NoZW1hdGljcyBhbHJlYWR5IHJlZ2lzdGVyZWRcIik7XG4gICAgfVxuICAgIGNvbmZpZ1NjaGVtYXRpY3NTZXQgPSB0cnVlO1xuICAgIHNlbGZSZWdpc3RyYXRpb25Ib3N0LnNldENvbmZpZ1NjaGVtYXRpY3MoY29uZmlnU2NoZW1hdGljcyk7XG4gICAgcmV0dXJuIHBsdWdpbkNvbnRleHQ7XG4gIH0sXG4gIHdpdGhHbG9iYWxDb25maWdTY2hlbWF0aWNzOiAoZ2xvYmFsQ29uZmlnU2NoZW1hdGljcykgPT4ge1xuICAgIGlmIChnbG9iYWxDb25maWdTY2hlbWF0aWNzU2V0KSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoXCJHbG9iYWwgY29uZmlnIHNjaGVtYXRpY3MgYWxyZWFkeSByZWdpc3RlcmVkXCIpO1xuICAgIH1cbiAgICBnbG9iYWxDb25maWdTY2hlbWF0aWNzU2V0ID0gdHJ1ZTtcbiAgICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5zZXRHbG9iYWxDb25maWdTY2hlbWF0aWNzKGdsb2JhbENvbmZpZ1NjaGVtYXRpY3MpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxuICB3aXRoVG9vbHNQcm92aWRlcjogKHRvb2xzUHJvdmlkZXIpID0+IHtcbiAgICBpZiAodG9vbHNQcm92aWRlclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiVG9vbHMgcHJvdmlkZXIgYWxyZWFkeSByZWdpc3RlcmVkXCIpO1xuICAgIH1cbiAgICBpZiAocHJlZGljdGlvbkxvb3BIYW5kbGVyU2V0KSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoXCJUb29scyBwcm92aWRlciBjYW5ub3QgYmUgdXNlZCB3aXRoIGEgcHJlZGljdGlvbkxvb3BIYW5kbGVyXCIpO1xuICAgIH1cblxuICAgIHRvb2xzUHJvdmlkZXJTZXQgPSB0cnVlO1xuICAgIHNlbGZSZWdpc3RyYXRpb25Ib3N0LnNldFRvb2xzUHJvdmlkZXIodG9vbHNQcm92aWRlcik7XG4gICAgcmV0dXJuIHBsdWdpbkNvbnRleHQ7XG4gIH0sXG4gIHdpdGhHZW5lcmF0b3I6IChnZW5lcmF0b3IpID0+IHtcbiAgICBpZiAoZ2VuZXJhdG9yU2V0KSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoXCJHZW5lcmF0b3IgYWxyZWFkeSByZWdpc3RlcmVkXCIpO1xuICAgIH1cblxuICAgIGdlbmVyYXRvclNldCA9IHRydWU7XG4gICAgc2VsZlJlZ2lzdHJhdGlvbkhvc3Quc2V0R2VuZXJhdG9yKGdlbmVyYXRvcik7XG4gICAgcmV0dXJuIHBsdWdpbkNvbnRleHQ7XG4gIH0sXG59O1xuXG5pbXBvcnQoXCIuLy4uL3NyYy9pbmRleC50c1wiKS50aGVuKGFzeW5jIG1vZHVsZSA9PiB7XG4gIHJldHVybiBhd2FpdCBtb2R1bGUubWFpbihwbHVnaW5Db250ZXh0KTtcbn0pLnRoZW4oKCkgPT4ge1xuICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5pbml0Q29tcGxldGVkKCk7XG59KS5jYXRjaCgoZXJyb3IpID0+IHtcbiAgY29uc29sZS5lcnJvcihcIkZhaWxlZCB0byBleGVjdXRlIHRoZSBtYWluIGZ1bmN0aW9uIG9mIHRoZSBwbHVnaW4uXCIpO1xuICBjb25zb2xlLmVycm9yKGVycm9yKTtcbn0pO1xuIl0sCiAgIm1hcHBpbmdzIjogIjs7Ozs7Ozs7Ozs7O0FBQUEsZ0JBRWE7QUFG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QUFBQSxFQUNUO0FBQUEsRUFDQSw0QkFBNEIsQ0FBQywyQkFBMkI7QUFDdEQsUUFBSSwyQkFBMkI7QUFDN0IsWUFBTSxJQUFJLE1BQU0sNkNBQTZDO0FBQUEsSUFDL0Q7QUFDQSxnQ0FBNEI7QUFDNUIseUJBQXFCLDBCQUEwQixzQkFBc0I7QUFDckUsV0FBTztBQUFBLEVBQ1Q7QUFBQSxFQUNBLG1CQUFtQixDQUFDLGtCQUFrQjtBQUNwQyxRQUFJLGtCQUFrQjtBQUNwQixZQUFNLElBQUksTUFBTSxtQ0FBbUM7QUFBQSxJQUNyRDtBQUNBLFFBQUksMEJBQTBCO0FBQzVCLFlBQU0sSUFBSSxNQUFNLDREQUE0RDtBQUFBLElBQzlFO0FBRUEsdUJBQW1CO0FBQ25CLHlCQUFxQixpQkFBaUIsYUFBYTtBQUNuRCxXQUFPO0FBQUEsRUFDVDtBQUFBLEVBQ0EsZUFBZSxDQUFDLGNBQWM7QUFDNUIsUUFBSSxjQUFjO0FBQ2hCLFlBQU0sSUFBSSxNQUFNLDhCQUE4QjtBQUFBLElBQ2hEO0FBRUEsbUJBQWU7QUFDZix5QkFBcUIsYUFBYSxTQUFTO0FBQzNDLFdBQU87QUFBQSxFQUNUO0FBQ0Y7QUFFQSx3REFBNEIsS0FBSyxPQUFNQyxZQUFVO0FBQy9DLFNBQU8sTUFBTUEsUUFBTyxLQUFLLGFBQWE7QUFDeEMsQ0FBQyxFQUFFLEtBQUssTUFBTTtBQUNaLHVCQUFxQixjQUFjO0FBQ3JDLENBQUMsRUFBRSxNQUFNLENBQUMsVUFBVTtBQUNsQixVQUFRLE1BQU0sb0RBQW9EO0FBQ2xFLFVBQVEsTUFBTSxLQUFLO0FBQ3JCLENBQUM7IiwKICAibmFtZXMiOiBbInJlc3VsdCIsICJjaG9zZW5TdHJhdGVneSIsICJpbXBvcnRfc2RrIiwgImltcG9ydF9zZGsiLCAicHJlcHJvY2VzcyIsICJjb25maWdTY2hlbWF0aWNzIiwgIm1vZHVsZSJdCn0K

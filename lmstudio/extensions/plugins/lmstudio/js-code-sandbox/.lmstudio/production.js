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

// C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/findLMStudioHome.ts
function findLMStudioHome() {
  if (lmstudioHome !== null) {
    return lmstudioHome;
  }
  const resolvedHomeDir = (0, import_fs.realpathSync)((0, import_os.homedir)());
  const pointerFilePath = (0, import_path.join)(resolvedHomeDir, ".lmstudio-home-pointer");
  if ((0, import_fs.existsSync)(pointerFilePath)) {
    lmstudioHome = (0, import_fs.readFileSync)(pointerFilePath, "utf-8").trim();
    return lmstudioHome;
  }
  const cacheHome = (0, import_path.join)(resolvedHomeDir, ".cache", "lm-studio");
  if ((0, import_fs.existsSync)(cacheHome)) {
    lmstudioHome = cacheHome;
    (0, import_fs.writeFileSync)(pointerFilePath, lmstudioHome, "utf-8");
    return lmstudioHome;
  }
  const home = (0, import_path.join)(resolvedHomeDir, ".lmstudio");
  lmstudioHome = home;
  (0, import_fs.writeFileSync)(pointerFilePath, lmstudioHome, "utf-8");
  return lmstudioHome;
}
var import_fs, import_os, import_path, lmstudioHome;
var init_findLMStudioHome = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/findLMStudioHome.ts"() {
    "use strict";
    import_fs = require("fs");
    import_os = require("os");
    import_path = require("path");
    lmstudioHome = null;
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/toolsProvider.ts
function getDenoPath() {
  const lmstudioHome2 = findLMStudioHome();
  const utilPath = (0, import_path2.join)(lmstudioHome2, ".internal", "utils");
  const denoPath = (0, import_path2.join)(utilPath, process.platform === "win32" ? "deno.exe" : "deno");
  return denoPath;
}
async function toolsProvider(ctl) {
  const tools = [];
  const createFileTool = (0, import_sdk.tool)({
    name: "run_javascript",
    description: import_sdk.text`
      Run a JavaScript code snippet using deno. You cannot import external modules but you have 
      read/write access to the current working directory.

      Pass the code you wish to run as a string in the 'javascript' parameter.

      By default, the code will timeout in 5 seconds. You can extend this timeout by setting the
      'timeout_seconds' parameter to a higher value in seconds, up to a maximum of 60 seconds.

      You will get the stdout and stderr output of the code execution, thus please print the output
      you wish to return using 'console.log' or 'console.error'.
    `,
    parameters: { javascript: import_zod.z.string(), timeout_seconds: import_zod.z.number().optional() },
    implementation: async ({ javascript, timeout_seconds }) => {
      const workingDirectory = ctl.getWorkingDirectory();
      const scriptFileName = `temp_script_${Date.now()}.ts`;
      const scriptFilePath = (0, import_path2.join)(workingDirectory, scriptFileName);
      await (0, import_promises.writeFile)(scriptFilePath, javascript, "utf-8");
      const childProcess = (0, import_child_process.spawn)(
        getDenoPath(),
        [
          "run",
          "--allow-read=.",
          "--allow-write=.",
          "--no-prompt",
          "--deny-net",
          "--deny-env",
          "--deny-sys",
          "--deny-run",
          "--deny-ffi",
          scriptFilePath
        ],
        {
          cwd: workingDirectory,
          timeout: (timeout_seconds ?? 5) * 1e3,
          // Convert seconds to milliseconds
          stdio: "pipe",
          env: {
            NO_COLOR: "true"
            // Disable color output in Deno
          }
        }
      );
      let stdout = "";
      let stderr = "";
      childProcess.stdout.setEncoding("utf-8");
      childProcess.stderr.setEncoding("utf-8");
      childProcess.stdout.on("data", (data) => {
        stdout += data;
      });
      childProcess.stderr.on("data", (data) => {
        stderr += data;
      });
      await new Promise((resolve, reject) => {
        childProcess.on("close", (code) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`Process exited with code ${code}. Stderr: ${stderr}`));
          }
        });
        childProcess.on("error", (err) => {
          reject(err);
        });
      });
      await (0, import_promises.rm)(scriptFilePath);
      return {
        stdout: stdout.trim(),
        stderr: stderr.trim()
      };
    }
  });
  tools.push(createFileTool);
  return tools;
}
var import_sdk, import_child_process, import_promises, import_path2, import_zod;
var init_toolsProvider = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/toolsProvider.ts"() {
    "use strict";
    import_sdk = require("@lmstudio/sdk");
    import_child_process = require("child_process");
    import_promises = require("fs/promises");
    import_path2 = require("path");
    import_zod = require("zod");
    init_findLMStudioHome();
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/index.ts
var src_exports = {};
__export(src_exports, {
  main: () => main
});
async function main(context) {
  context.withToolsProvider(toolsProvider);
}
var init_src = __esm({
  "C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/src/index.ts"() {
    "use strict";
    init_toolsProvider();
  }
});

// C:/Users/RUNNER~1/AppData/Local/Temp/5f94cfd2e5cd6e453ad527f5aafecffe/.lmstudio/entry.ts
var import_sdk2 = require("@lmstudio/sdk");
var clientIdentifier = process.env.LMS_PLUGIN_CLIENT_IDENTIFIER;
var clientPasskey = process.env.LMS_PLUGIN_CLIENT_PASSKEY;
var baseUrl = process.env.LMS_PLUGIN_BASE_URL;
var client = new import_sdk2.LMStudioClient({
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
  withPromptPreprocessor: (preprocess) => {
    if (promptPreprocessorSet) {
      throw new Error("PromptPreprocessor already registered");
    }
    promptPreprocessorSet = true;
    selfRegistrationHost.setPromptPreprocessor(preprocess);
    return pluginContext;
  },
  withConfigSchematics: (configSchematics) => {
    if (configSchematicsSet) {
      throw new Error("Config schematics already registered");
    }
    configSchematicsSet = true;
    selfRegistrationHost.setConfigSchematics(configSchematics);
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
  withToolsProvider: (toolsProvider2) => {
    if (toolsProviderSet) {
      throw new Error("Tools provider already registered");
    }
    if (predictionLoopHandlerSet) {
      throw new Error("Tools provider cannot be used with a predictionLoopHandler");
    }
    toolsProviderSet = true;
    selfRegistrationHost.setToolsProvider(toolsProvider2);
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vc3JjL2ZpbmRMTVN0dWRpb0hvbWUudHMiLCAiLi4vc3JjL3Rvb2xzUHJvdmlkZXIudHMiLCAiLi4vc3JjL2luZGV4LnRzIiwgImVudHJ5LnRzIl0sCiAgInNvdXJjZXNDb250ZW50IjogWyJpbXBvcnQgeyBleGlzdHNTeW5jLCByZWFkRmlsZVN5bmMsIHJlYWxwYXRoU3luYywgd3JpdGVGaWxlU3luYyB9IGZyb20gXCJmc1wiO1xyXG5pbXBvcnQgeyBob21lZGlyIH0gZnJvbSBcIm9zXCI7XHJcbmltcG9ydCB7IGpvaW4gfSBmcm9tIFwicGF0aFwiO1xyXG5cclxubGV0IGxtc3R1ZGlvSG9tZTogc3RyaW5nIHwgbnVsbCA9IG51bGw7XHJcblxyXG5leHBvcnQgZnVuY3Rpb24gZmluZExNU3R1ZGlvSG9tZSgpIHtcclxuICBpZiAobG1zdHVkaW9Ib21lICE9PSBudWxsKSB7XHJcbiAgICByZXR1cm4gbG1zdHVkaW9Ib21lO1xyXG4gIH1cclxuXHJcbiAgLy8gaWYgYXBwbGljYWJsZSwgY29udmVydCByZWxhdGl2ZSBwYXRoIHRvIGFic29sdXRlIGFuZCBmb2xsb3cgdGhlIHN5bWxpbmtcclxuICBjb25zdCByZXNvbHZlZEhvbWVEaXIgPSByZWFscGF0aFN5bmMoaG9tZWRpcigpKTtcclxuXHJcbiAgY29uc3QgcG9pbnRlckZpbGVQYXRoID0gam9pbihyZXNvbHZlZEhvbWVEaXIsIFwiLmxtc3R1ZGlvLWhvbWUtcG9pbnRlclwiKTtcclxuICBpZiAoZXhpc3RzU3luYyhwb2ludGVyRmlsZVBhdGgpKSB7XHJcbiAgICBsbXN0dWRpb0hvbWUgPSByZWFkRmlsZVN5bmMocG9pbnRlckZpbGVQYXRoLCBcInV0Zi04XCIpLnRyaW0oKTtcclxuICAgIHJldHVybiBsbXN0dWRpb0hvbWU7XHJcbiAgfVxyXG5cclxuICAvLyBTZWUgaWYgfi8uY2FjaGUvbG0tc3R1ZGlvIGV4aXN0cy4gSWYgaXQgZG9lcywgdXNlIGl0LlxyXG4gIGNvbnN0IGNhY2hlSG9tZSA9IGpvaW4ocmVzb2x2ZWRIb21lRGlyLCBcIi5jYWNoZVwiLCBcImxtLXN0dWRpb1wiKTtcclxuICBpZiAoZXhpc3RzU3luYyhjYWNoZUhvbWUpKSB7XHJcbiAgICBsbXN0dWRpb0hvbWUgPSBjYWNoZUhvbWU7XHJcbiAgICB3cml0ZUZpbGVTeW5jKHBvaW50ZXJGaWxlUGF0aCwgbG1zdHVkaW9Ib21lLCBcInV0Zi04XCIpO1xyXG4gICAgcmV0dXJuIGxtc3R1ZGlvSG9tZTtcclxuICB9XHJcblxyXG4gIC8vIE90aGVyd2lzZSwgZmFsbGJhY2sgdG8gfi8ubG1zdHVkaW9cclxuICBjb25zdCBob21lID0gam9pbihyZXNvbHZlZEhvbWVEaXIsIFwiLmxtc3R1ZGlvXCIpO1xyXG4gIGxtc3R1ZGlvSG9tZSA9IGhvbWU7XHJcbiAgd3JpdGVGaWxlU3luYyhwb2ludGVyRmlsZVBhdGgsIGxtc3R1ZGlvSG9tZSwgXCJ1dGYtOFwiKTtcclxuICByZXR1cm4gbG1zdHVkaW9Ib21lO1xyXG59XHJcbiIsICJpbXBvcnQgeyB0ZXh0LCB0b29sLCB0eXBlIFRvb2wsIHR5cGUgVG9vbHNQcm92aWRlckNvbnRyb2xsZXIgfSBmcm9tIFwiQGxtc3R1ZGlvL3Nka1wiO1xyXG5pbXBvcnQgeyBzcGF3biB9IGZyb20gXCJjaGlsZF9wcm9jZXNzXCI7XHJcbmltcG9ydCB7IHJtLCB3cml0ZUZpbGUgfSBmcm9tIFwiZnMvcHJvbWlzZXNcIjtcclxuaW1wb3J0IHsgam9pbiB9IGZyb20gXCJwYXRoXCI7XHJcbmltcG9ydCB7IHogfSBmcm9tIFwiem9kXCI7XHJcbmltcG9ydCB7IGZpbmRMTVN0dWRpb0hvbWUgfSBmcm9tIFwiLi9maW5kTE1TdHVkaW9Ib21lXCI7XHJcblxyXG5mdW5jdGlvbiBnZXREZW5vUGF0aCgpIHtcclxuICBjb25zdCBsbXN0dWRpb0hvbWUgPSBmaW5kTE1TdHVkaW9Ib21lKCk7XHJcbiAgY29uc3QgdXRpbFBhdGggPSBqb2luKGxtc3R1ZGlvSG9tZSwgXCIuaW50ZXJuYWxcIiwgXCJ1dGlsc1wiKTtcclxuICBjb25zdCBkZW5vUGF0aCA9IGpvaW4odXRpbFBhdGgsIHByb2Nlc3MucGxhdGZvcm0gPT09IFwid2luMzJcIiA/IFwiZGVuby5leGVcIiA6IFwiZGVub1wiKTtcclxuICByZXR1cm4gZGVub1BhdGg7XHJcbn1cclxuXHJcbmV4cG9ydCBhc3luYyBmdW5jdGlvbiB0b29sc1Byb3ZpZGVyKGN0bDogVG9vbHNQcm92aWRlckNvbnRyb2xsZXIpIHtcclxuICBjb25zdCB0b29sczogVG9vbFtdID0gW107XHJcblxyXG4gIGNvbnN0IGNyZWF0ZUZpbGVUb29sID0gdG9vbCh7XHJcbiAgICBuYW1lOiBcInJ1bl9qYXZhc2NyaXB0XCIsXHJcbiAgICBkZXNjcmlwdGlvbjogdGV4dGBcclxuICAgICAgUnVuIGEgSmF2YVNjcmlwdCBjb2RlIHNuaXBwZXQgdXNpbmcgZGVuby4gWW91IGNhbm5vdCBpbXBvcnQgZXh0ZXJuYWwgbW9kdWxlcyBidXQgeW91IGhhdmUgXHJcbiAgICAgIHJlYWQvd3JpdGUgYWNjZXNzIHRvIHRoZSBjdXJyZW50IHdvcmtpbmcgZGlyZWN0b3J5LlxyXG5cclxuICAgICAgUGFzcyB0aGUgY29kZSB5b3Ugd2lzaCB0byBydW4gYXMgYSBzdHJpbmcgaW4gdGhlICdqYXZhc2NyaXB0JyBwYXJhbWV0ZXIuXHJcblxyXG4gICAgICBCeSBkZWZhdWx0LCB0aGUgY29kZSB3aWxsIHRpbWVvdXQgaW4gNSBzZWNvbmRzLiBZb3UgY2FuIGV4dGVuZCB0aGlzIHRpbWVvdXQgYnkgc2V0dGluZyB0aGVcclxuICAgICAgJ3RpbWVvdXRfc2Vjb25kcycgcGFyYW1ldGVyIHRvIGEgaGlnaGVyIHZhbHVlIGluIHNlY29uZHMsIHVwIHRvIGEgbWF4aW11bSBvZiA2MCBzZWNvbmRzLlxyXG5cclxuICAgICAgWW91IHdpbGwgZ2V0IHRoZSBzdGRvdXQgYW5kIHN0ZGVyciBvdXRwdXQgb2YgdGhlIGNvZGUgZXhlY3V0aW9uLCB0aHVzIHBsZWFzZSBwcmludCB0aGUgb3V0cHV0XHJcbiAgICAgIHlvdSB3aXNoIHRvIHJldHVybiB1c2luZyAnY29uc29sZS5sb2cnIG9yICdjb25zb2xlLmVycm9yJy5cclxuICAgIGAsXHJcbiAgICBwYXJhbWV0ZXJzOiB7IGphdmFzY3JpcHQ6IHouc3RyaW5nKCksIHRpbWVvdXRfc2Vjb25kczogei5udW1iZXIoKS5vcHRpb25hbCgpIH0sXHJcbiAgICBpbXBsZW1lbnRhdGlvbjogYXN5bmMgKHsgamF2YXNjcmlwdCwgdGltZW91dF9zZWNvbmRzIH0pID0+IHtcclxuICAgICAgY29uc3Qgd29ya2luZ0RpcmVjdG9yeSA9IGN0bC5nZXRXb3JraW5nRGlyZWN0b3J5KCk7XHJcbiAgICAgIGNvbnN0IHNjcmlwdEZpbGVOYW1lID0gYHRlbXBfc2NyaXB0XyR7RGF0ZS5ub3coKX0udHNgO1xyXG4gICAgICBjb25zdCBzY3JpcHRGaWxlUGF0aCA9IGpvaW4od29ya2luZ0RpcmVjdG9yeSwgc2NyaXB0RmlsZU5hbWUpO1xyXG4gICAgICBhd2FpdCB3cml0ZUZpbGUoc2NyaXB0RmlsZVBhdGgsIGphdmFzY3JpcHQsIFwidXRmLThcIik7XHJcblxyXG4gICAgICBjb25zdCBjaGlsZFByb2Nlc3MgPSBzcGF3bihcclxuICAgICAgICBnZXREZW5vUGF0aCgpLFxyXG4gICAgICAgIFtcclxuICAgICAgICAgIFwicnVuXCIsXHJcbiAgICAgICAgICBcIi0tYWxsb3ctcmVhZD0uXCIsXHJcbiAgICAgICAgICBcIi0tYWxsb3ctd3JpdGU9LlwiLFxyXG4gICAgICAgICAgXCItLW5vLXByb21wdFwiLFxyXG4gICAgICAgICAgXCItLWRlbnktbmV0XCIsXHJcbiAgICAgICAgICBcIi0tZGVueS1lbnZcIixcclxuICAgICAgICAgIFwiLS1kZW55LXN5c1wiLFxyXG4gICAgICAgICAgXCItLWRlbnktcnVuXCIsXHJcbiAgICAgICAgICBcIi0tZGVueS1mZmlcIixcclxuICAgICAgICAgIHNjcmlwdEZpbGVQYXRoLFxyXG4gICAgICAgIF0sXHJcbiAgICAgICAge1xyXG4gICAgICAgICAgY3dkOiB3b3JraW5nRGlyZWN0b3J5LFxyXG4gICAgICAgICAgdGltZW91dDogKHRpbWVvdXRfc2Vjb25kcyA/PyA1KSAqIDEwMDAsIC8vIENvbnZlcnQgc2Vjb25kcyB0byBtaWxsaXNlY29uZHNcclxuICAgICAgICAgIHN0ZGlvOiBcInBpcGVcIixcclxuICAgICAgICAgIGVudjoge1xyXG4gICAgICAgICAgICBOT19DT0xPUjogXCJ0cnVlXCIsIC8vIERpc2FibGUgY29sb3Igb3V0cHV0IGluIERlbm9cclxuICAgICAgICAgIH0sXHJcbiAgICAgICAgfSxcclxuICAgICAgKTtcclxuXHJcbiAgICAgIGxldCBzdGRvdXQgPSBcIlwiO1xyXG4gICAgICBsZXQgc3RkZXJyID0gXCJcIjtcclxuXHJcbiAgICAgIGNoaWxkUHJvY2Vzcy5zdGRvdXQuc2V0RW5jb2RpbmcoXCJ1dGYtOFwiKTtcclxuICAgICAgY2hpbGRQcm9jZXNzLnN0ZGVyci5zZXRFbmNvZGluZyhcInV0Zi04XCIpO1xyXG5cclxuICAgICAgY2hpbGRQcm9jZXNzLnN0ZG91dC5vbihcImRhdGFcIiwgZGF0YSA9PiB7XHJcbiAgICAgICAgc3Rkb3V0ICs9IGRhdGE7XHJcbiAgICAgIH0pO1xyXG4gICAgICBjaGlsZFByb2Nlc3Muc3RkZXJyLm9uKFwiZGF0YVwiLCBkYXRhID0+IHtcclxuICAgICAgICBzdGRlcnIgKz0gZGF0YTtcclxuICAgICAgfSk7XHJcblxyXG4gICAgICBhd2FpdCBuZXcgUHJvbWlzZTx2b2lkPigocmVzb2x2ZSwgcmVqZWN0KSA9PiB7XHJcbiAgICAgICAgY2hpbGRQcm9jZXNzLm9uKFwiY2xvc2VcIiwgY29kZSA9PiB7XHJcbiAgICAgICAgICBpZiAoY29kZSA9PT0gMCkge1xyXG4gICAgICAgICAgICByZXNvbHZlKCk7XHJcbiAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICByZWplY3QobmV3IEVycm9yKGBQcm9jZXNzIGV4aXRlZCB3aXRoIGNvZGUgJHtjb2RlfS4gU3RkZXJyOiAke3N0ZGVycn1gKSk7XHJcbiAgICAgICAgICB9XHJcbiAgICAgICAgfSk7XHJcblxyXG4gICAgICAgIGNoaWxkUHJvY2Vzcy5vbihcImVycm9yXCIsIGVyciA9PiB7XHJcbiAgICAgICAgICByZWplY3QoZXJyKTtcclxuICAgICAgICB9KTtcclxuICAgICAgfSk7XHJcblxyXG4gICAgICBhd2FpdCBybShzY3JpcHRGaWxlUGF0aCk7XHJcblxyXG4gICAgICByZXR1cm4ge1xyXG4gICAgICAgIHN0ZG91dDogc3Rkb3V0LnRyaW0oKSxcclxuICAgICAgICBzdGRlcnI6IHN0ZGVyci50cmltKCksXHJcbiAgICAgIH07XHJcbiAgICB9LFxyXG4gIH0pO1xyXG4gIHRvb2xzLnB1c2goY3JlYXRlRmlsZVRvb2wpO1xyXG5cclxuICByZXR1cm4gdG9vbHM7XHJcbn1cclxuIiwgImltcG9ydCB7IHR5cGUgUGx1Z2luQ29udGV4dCB9IGZyb20gXCJAbG1zdHVkaW8vc2RrXCI7XHJcbmltcG9ydCB7IHRvb2xzUHJvdmlkZXIgfSBmcm9tIFwiLi90b29sc1Byb3ZpZGVyXCI7XHJcblxyXG5leHBvcnQgYXN5bmMgZnVuY3Rpb24gbWFpbihjb250ZXh0OiBQbHVnaW5Db250ZXh0KSB7XHJcbiAgLy8gUmVnaXN0ZXIgdGhlIHRvb2xzIHByb3ZpZGVyLlxyXG4gIGNvbnRleHQud2l0aFRvb2xzUHJvdmlkZXIodG9vbHNQcm92aWRlcik7XHJcbn1cclxuIiwgImltcG9ydCB7IExNU3R1ZGlvQ2xpZW50LCB0eXBlIFBsdWdpbkNvbnRleHQgfSBmcm9tIFwiQGxtc3R1ZGlvL3Nka1wiO1xuXG5kZWNsYXJlIHZhciBwcm9jZXNzOiBhbnk7XG5cbi8vIFdlIHJlY2VpdmUgcnVudGltZSBpbmZvcm1hdGlvbiBpbiB0aGUgZW52aXJvbm1lbnQgdmFyaWFibGVzLlxuY29uc3QgY2xpZW50SWRlbnRpZmllciA9IHByb2Nlc3MuZW52LkxNU19QTFVHSU5fQ0xJRU5UX0lERU5USUZJRVI7XG5jb25zdCBjbGllbnRQYXNza2V5ID0gcHJvY2Vzcy5lbnYuTE1TX1BMVUdJTl9DTElFTlRfUEFTU0tFWTtcbmNvbnN0IGJhc2VVcmwgPSBwcm9jZXNzLmVudi5MTVNfUExVR0lOX0JBU0VfVVJMO1xuXG5jb25zdCBjbGllbnQgPSBuZXcgTE1TdHVkaW9DbGllbnQoe1xuICBjbGllbnRJZGVudGlmaWVyLFxuICBjbGllbnRQYXNza2V5LFxuICBiYXNlVXJsLFxufSk7XG5cbihnbG9iYWxUaGlzIGFzIGFueSkuX19MTVNfUExVR0lOX0NPTlRFWFQgPSB0cnVlO1xuXG5sZXQgcHJlZGljdGlvbkxvb3BIYW5kbGVyU2V0ID0gZmFsc2U7XG5sZXQgcHJvbXB0UHJlcHJvY2Vzc29yU2V0ID0gZmFsc2U7XG5sZXQgY29uZmlnU2NoZW1hdGljc1NldCA9IGZhbHNlO1xubGV0IGdsb2JhbENvbmZpZ1NjaGVtYXRpY3NTZXQgPSBmYWxzZTtcbmxldCB0b29sc1Byb3ZpZGVyU2V0ID0gZmFsc2U7XG5sZXQgZ2VuZXJhdG9yU2V0ID0gZmFsc2U7XG5cbmNvbnN0IHNlbGZSZWdpc3RyYXRpb25Ib3N0ID0gY2xpZW50LnBsdWdpbnMuZ2V0U2VsZlJlZ2lzdHJhdGlvbkhvc3QoKTtcblxuY29uc3QgcGx1Z2luQ29udGV4dDogUGx1Z2luQ29udGV4dCA9IHtcbiAgd2l0aFByZWRpY3Rpb25Mb29wSGFuZGxlcjogKGdlbmVyYXRlKSA9PiB7XG4gICAgaWYgKHByZWRpY3Rpb25Mb29wSGFuZGxlclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiUHJlZGljdGlvbkxvb3BIYW5kbGVyIGFscmVhZHkgcmVnaXN0ZXJlZFwiKTtcbiAgICB9XG4gICAgaWYgKHRvb2xzUHJvdmlkZXJTZXQpIHtcbiAgICAgIHRocm93IG5ldyBFcnJvcihcIlByZWRpY3Rpb25Mb29wSGFuZGxlciBjYW5ub3QgYmUgdXNlZCB3aXRoIGEgdG9vbHMgcHJvdmlkZXJcIik7XG4gICAgfVxuXG4gICAgcHJlZGljdGlvbkxvb3BIYW5kbGVyU2V0ID0gdHJ1ZTtcbiAgICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5zZXRQcmVkaWN0aW9uTG9vcEhhbmRsZXIoZ2VuZXJhdGUpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxuICB3aXRoUHJvbXB0UHJlcHJvY2Vzc29yOiAocHJlcHJvY2VzcykgPT4ge1xuICAgIGlmIChwcm9tcHRQcmVwcm9jZXNzb3JTZXQpIHtcbiAgICAgIHRocm93IG5ldyBFcnJvcihcIlByb21wdFByZXByb2Nlc3NvciBhbHJlYWR5IHJlZ2lzdGVyZWRcIik7XG4gICAgfVxuICAgIHByb21wdFByZXByb2Nlc3NvclNldCA9IHRydWU7XG4gICAgc2VsZlJlZ2lzdHJhdGlvbkhvc3Quc2V0UHJvbXB0UHJlcHJvY2Vzc29yKHByZXByb2Nlc3MpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxuICB3aXRoQ29uZmlnU2NoZW1hdGljczogKGNvbmZpZ1NjaGVtYXRpY3MpID0+IHtcbiAgICBpZiAoY29uZmlnU2NoZW1hdGljc1NldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiQ29uZmlnIHNjaGVtYXRpY3MgYWxyZWFkeSByZWdpc3RlcmVkXCIpO1xuICAgIH1cbiAgICBjb25maWdTY2hlbWF0aWNzU2V0ID0gdHJ1ZTtcbiAgICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5zZXRDb25maWdTY2hlbWF0aWNzKGNvbmZpZ1NjaGVtYXRpY3MpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxuICB3aXRoR2xvYmFsQ29uZmlnU2NoZW1hdGljczogKGdsb2JhbENvbmZpZ1NjaGVtYXRpY3MpID0+IHtcbiAgICBpZiAoZ2xvYmFsQ29uZmlnU2NoZW1hdGljc1NldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiR2xvYmFsIGNvbmZpZyBzY2hlbWF0aWNzIGFscmVhZHkgcmVnaXN0ZXJlZFwiKTtcbiAgICB9XG4gICAgZ2xvYmFsQ29uZmlnU2NoZW1hdGljc1NldCA9IHRydWU7XG4gICAgc2VsZlJlZ2lzdHJhdGlvbkhvc3Quc2V0R2xvYmFsQ29uZmlnU2NoZW1hdGljcyhnbG9iYWxDb25maWdTY2hlbWF0aWNzKTtcbiAgICByZXR1cm4gcGx1Z2luQ29udGV4dDtcbiAgfSxcbiAgd2l0aFRvb2xzUHJvdmlkZXI6ICh0b29sc1Byb3ZpZGVyKSA9PiB7XG4gICAgaWYgKHRvb2xzUHJvdmlkZXJTZXQpIHtcbiAgICAgIHRocm93IG5ldyBFcnJvcihcIlRvb2xzIHByb3ZpZGVyIGFscmVhZHkgcmVnaXN0ZXJlZFwiKTtcbiAgICB9XG4gICAgaWYgKHByZWRpY3Rpb25Mb29wSGFuZGxlclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiVG9vbHMgcHJvdmlkZXIgY2Fubm90IGJlIHVzZWQgd2l0aCBhIHByZWRpY3Rpb25Mb29wSGFuZGxlclwiKTtcbiAgICB9XG5cbiAgICB0b29sc1Byb3ZpZGVyU2V0ID0gdHJ1ZTtcbiAgICBzZWxmUmVnaXN0cmF0aW9uSG9zdC5zZXRUb29sc1Byb3ZpZGVyKHRvb2xzUHJvdmlkZXIpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxuICB3aXRoR2VuZXJhdG9yOiAoZ2VuZXJhdG9yKSA9PiB7XG4gICAgaWYgKGdlbmVyYXRvclNldCkge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKFwiR2VuZXJhdG9yIGFscmVhZHkgcmVnaXN0ZXJlZFwiKTtcbiAgICB9XG5cbiAgICBnZW5lcmF0b3JTZXQgPSB0cnVlO1xuICAgIHNlbGZSZWdpc3RyYXRpb25Ib3N0LnNldEdlbmVyYXRvcihnZW5lcmF0b3IpO1xuICAgIHJldHVybiBwbHVnaW5Db250ZXh0O1xuICB9LFxufTtcblxuaW1wb3J0KFwiLi8uLi9zcmMvaW5kZXgudHNcIikudGhlbihhc3luYyBtb2R1bGUgPT4ge1xuICByZXR1cm4gYXdhaXQgbW9kdWxlLm1haW4ocGx1Z2luQ29udGV4dCk7XG59KS50aGVuKCgpID0+IHtcbiAgc2VsZlJlZ2lzdHJhdGlvbkhvc3QuaW5pdENvbXBsZXRlZCgpO1xufSkuY2F0Y2goKGVycm9yKSA9PiB7XG4gIGNvbnNvbGUuZXJyb3IoXCJGYWlsZWQgdG8gZXhlY3V0ZSB0aGUgbWFpbiBmdW5jdGlvbiBvZiB0aGUgcGx1Z2luLlwiKTtcbiAgY29uc29sZS5lcnJvcihlcnJvcik7XG59KTtcbiJdLAogICJtYXBwaW5ncyI6ICI7Ozs7Ozs7Ozs7OztBQU1PLFNBQVMsbUJBQW1CO0FBQ2pDLE1BQUksaUJBQWlCLE1BQU07QUFDekIsV0FBTztBQUFBLEVBQ1Q7QUFHQSxRQUFNLHNCQUFrQiw0QkFBYSxtQkFBUSxDQUFDO0FBRTlDLFFBQU0sc0JBQWtCLGtCQUFLLGlCQUFpQix3QkFBd0I7QUFDdEUsVUFBSSxzQkFBVyxlQUFlLEdBQUc7QUFDL0IsdUJBQWUsd0JBQWEsaUJBQWlCLE9BQU8sRUFBRSxLQUFLO0FBQzNELFdBQU87QUFBQSxFQUNUO0FBR0EsUUFBTSxnQkFBWSxrQkFBSyxpQkFBaUIsVUFBVSxXQUFXO0FBQzdELFVBQUksc0JBQVcsU0FBUyxHQUFHO0FBQ3pCLG1CQUFlO0FBQ2YsaUNBQWMsaUJBQWlCLGNBQWMsT0FBTztBQUNwRCxXQUFPO0FBQUEsRUFDVDtBQUdBLFFBQU0sV0FBTyxrQkFBSyxpQkFBaUIsV0FBVztBQUM5QyxpQkFBZTtBQUNmLCtCQUFjLGlCQUFpQixjQUFjLE9BQU87QUFDcEQsU0FBTztBQUNUO0FBakNBLGVBQ0EsV0FDQSxhQUVJO0FBSko7QUFBQTtBQUFBO0FBQUEsZ0JBQXNFO0FBQ3RFLGdCQUF3QjtBQUN4QixrQkFBcUI7QUFFckIsSUFBSSxlQUE4QjtBQUFBO0FBQUE7OztBQ0dsQyxTQUFTLGNBQWM7QUFDckIsUUFBTUEsZ0JBQWUsaUJBQWlCO0FBQ3RDLFFBQU0sZUFBVyxtQkFBS0EsZUFBYyxhQUFhLE9BQU87QUFDeEQsUUFBTSxlQUFXLG1CQUFLLFVBQVUsUUFBUSxhQUFhLFVBQVUsYUFBYSxNQUFNO0FBQ2xGLFNBQU87QUFDVDtBQUVBLGVBQXNCLGNBQWMsS0FBOEI7QUFDaEUsUUFBTSxRQUFnQixDQUFDO0FBRXZCLFFBQU0scUJBQWlCLGlCQUFLO0FBQUEsSUFDMUIsTUFBTTtBQUFBLElBQ04sYUFBYTtB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QSxFQUNuQywyQkFBMkIsQ0FBQyxhQUFhO0FBQ3ZDLFFBQUksMEJBQTBCO0FBQzVCLFlBQU0sSUFBSSxNQUFNLDBDQUEwQztBQUFBLElBQzVEO0FBQ0EsUUFBSSxrQkFBa0I7QUFDcEIsWUFBTSxJQUFJLE1BQU0sNERBQTREO0FBQUEsSUFDOUU7QUFFQSwrQkFBMkI7QUFDM0IseUJBQXFCLHlCQUF5QixRQUFRO0FBQ3RELFdBQU87QUFBQSxFQUNUO0FBQUEsRUFDQSx3QkFBd0IsQ0FBQyxlQUFlO0FBQ3RDLFFBQUksdUJBQXVCO0FBQ3pCLFlBQU0sSUFBSSxNQUFNLHVDQUF1QztBQUFBLElBQ3pEO0FBQ0EsNEJBQXdCO0FBQ3hCLHlCQUFxQixzQkFBc0IsVUFBVTtBQUNyRCxXQUFPO0FBQUEsRUFDVDtBQUFBLEVBQ0Esc0JBQXNCLENBQUMscUJBQXFCO0FBQzFDLFFBQUkscUJBQXFCO0FBQ3ZCLFlBQU0sSUFBSSxNQUFNLHNDQUFzQztBQUFBLElBQ3hEO0FBQ0EsMEJBQXNCO0FBQ3RCLHlCQUFxQixvQkFBb0IsZ0JBQWdCO0FBQ3pELFdBQU87QUFBQSxFQUNUO0FBQUEsRUFDQSw0QkFBNEIsQ0FBQywyQkFBMkI7QUFDdEQsUUFBSSwyQkFBMkI7QUFDN0IsWUFBTSxJQUFJLE1BQU0sNkNBQTZDO0FBQUEsSUFDL0Q7QUFDQSxnQ0FBNEI7QUFDNUIseUJBQXFCLDBCQUEwQixzQkFBc0I7QUFDckUsV0FBTztBQUFBLEVBQ1Q7QUFBQSxFQUNBLG1CQUFtQixDQUFDQyxtQkFBa0I7QUFDcEMsUUFBSSxrQkFBa0I7QUFDcEIsWUFBTSxJQUFJLE1BQU0sbUNBQW1DO0FBQUEsSUFDckQ7QUFDQSxRQUFJLDBCQUEwQjtBQUM1QixZQUFNLElBQUksTUFBTSw0REFBNEQ7QUFBQSxJQUM5RTtBQUVBLHVCQUFtQjtBQUNuQix5QkFBcUIsaUJBQWlCQSxjQUFhO0FBQ25ELFdBQU87QUFBQSxFQUNUO0FBQUEsRUFDQSxlQUFlLENBQUMsY0FBYztBQUM1QixRQUFJLGNBQWM7QUFDaEIsWUFBTSxJQUFJLE1BQU0sOEJBQThCO0FBQUEsSUFDaEQ7QUFFQSxtQkFBZTtBQUNmLHlCQUFxQixhQUFhLFNBQVM7QUFDM0MsV0FBTztBQUFBLEVBQ1Q7QUFDRjtBQUVBLHdEQUE0QixLQUFLLE9BQU1DLFlBQVU7QUFDL0MsU0FBTyxNQUFNQSxRQUFPLEtBQUssYUFBYTtBQUN4QyxDQUFDLEVBQUUsS0FBSyxNQUFNO0FBQ1osdUJBQXFCLGNBQWM7QUFDckMsQ0FBQyxFQUFFLE1BQU0sQ0FBQyxVQUFVO0FBQ2xCLFVBQVEsTUFBTSxvREFBb0Q7QUFDbEUsVUFBUSxNQUFNLEtBQUs7QUFDckIsQ0FBQzsiLAogICJuYW1lcyI6IFsibG1zdHVkaW9Ib21lIiwgImltcG9ydF9wYXRoIiwgImltcG9ydF9zZGsiLCAidG9vbHNQcm92aWRlciIsICJtb2R1bGUiXQp9Cg==

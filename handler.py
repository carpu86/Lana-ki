import runpod

def handler(job):
    """
    Das ist der Einstiegspunkt für RunPod.
    Hier wird später die Video/Bild-Generierung aufgerufen.
    """
    job_input = job.get("input", {})
    task = job_input.get("task", "unknown")
    
    print(f"Lana Node C: Empfange Task -> {task}")
    
    # Simpler Ping-Pong Test für das Setup
    if task == "ping":
        return {"status": "success", "message": "Lana Node C (RunPod) ist online und einsatzbereit!"}
        
    return {"status": "error", "error": "Unbekannter Task"}

# Starte den Serverless Listener
runpod.serverless.start({"handler": handler})

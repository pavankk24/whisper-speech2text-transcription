let mediaRecorder;
let audioChunks = [];

document.getElementById("start").onclick = async () => {
    audioChunks = [];

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

        const response = await fetch("/transcribe", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        document.getElementById("transcript").textContent = data.transcription || "[Error]";
        document.getElementById("latency").textContent = data.latency || "N/A";
    };

    mediaRecorder.start();
    document.getElementById("start").disabled = true;
    document.getElementById("stop").disabled = false;
};

document.getElementById("stop").onclick = () => {
    mediaRecorder.stop();
    document.getElementById("start").disabled = false;
    document.getElementById("stop").disabled = true;
};

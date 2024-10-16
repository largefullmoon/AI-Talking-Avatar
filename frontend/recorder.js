let recorder;
let audioBlob;
async function startRecording() {
    // Get access to the user's microphone
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Create a new RecordRTC instance
    recorder = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/webm',  // RecordRTC will handle conversion to .mp3
        desiredSampRate: 16000,  // Specify sampling rate
        recorderType: RecordRTC.StereoAudioRecorder,
        numberOfAudioChannels: 1  // Mono channel
    });

    // Start recording
    recorder.startRecording();

    // Update button states
    startBtn.disabled = true;
    stopBtn.disabled = false;
}

function stopRecording() {
    recorder.stopRecording(() => {
        audioBlob = recorder.getBlob();
        // const audioURL = URL.createObjectURL(audioBlob);
        // audioElement.src = audioURL;
        // downloadBtn.disabled = false;

        // Send the audio file to the backend for processing
        sendAudioToBackend(audioBlob);
    });
}

function downloadAudio() {
    // Create an anchor element to download the .mp3 file
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(audioBlob);
    downloadLink.download = 'audio.mp3';  // Set the file name and format
    downloadLink.click();
}


async function sendAudioToBackend(audioBlob) {
    // Prepare FormData to send the audio blob
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.mp3');

    try {
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        });
        const audioBlob = await response.blob();
        // Create an object URL for the audio file
        const audioUrl = URL.createObjectURL(audioBlob);
        // Set the source of the audio element and play the audio
        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = audioUrl;
        audioPlayer.play();
    } catch (error) {
        console.error('Error sending audio to backend:', error);
    }
}

// const audio = new Audio('path/to/speech.mp3');
// audio.play();

// // Sync viseme animations with audio
// const visemeTimings = [
//     { time: 0.1, viseme: 'a' },
//     { time: 0.3, viseme: 'o' },
//     // ...more viseme timings from the TTS service
// ];

// audio.addEventListener('timeupdate', () => {
//     const currentTime = audio.currentTime;
//     const currentViseme = visemeTimings.find(v => v.time <= currentTime);

//     if (currentViseme) {
//         resetVisemes();
//         applyViseme(currentViseme.viseme);
//     }
// });

// audio.addEventListener('ended', () => {
//     resetVisemes();
// });
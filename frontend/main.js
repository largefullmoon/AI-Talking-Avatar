import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

const canvas = document.getElementById('renderCanvas');
const engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });

let scene, camera, mesh, animationGroup, isAnimating = false, sound;
const uploadButton = document.getElementById('upload');
let teethMesh, tongueMesh, headMesh;
const createScene = function () {
    console.log("Creating scene...");
    scene = new BABYLON.Scene(engine);

    const hdrTexture = BABYLON.CubeTexture.CreateFromPrefilteredData("./assets/environment.env", scene);
    scene.environmentTexture = hdrTexture;

    scene.clearColor = new BABYLON.Color4(0.8, 0.8, 0.8, 1);

    const ground = BABYLON.MeshBuilder.CreateGround("ground", { width: 100, height: 100 }, scene);
    const groundMaterial = new BABYLON.StandardMaterial("groundMat", scene);
    groundMaterial.diffuseColor = new BABYLON.Color3(0.5, 0.5, 0.5);
    groundMaterial.alpha = 0.0;
    ground.material = groundMaterial;
    ground.receiveShadows = false;

    const light = new BABYLON.DirectionalLight("dirLight", new BABYLON.Vector3(-1, -2, -1), scene);
    light.position = new BABYLON.Vector3(20, 40, 20);

    const shadowGenerator = new BABYLON.ShadowGenerator(2048, light);
    shadowGenerator.useExponentialShadowMap = true;

    camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, new BABYLON.Vector3(0, 0, 0), scene);
    camera.attachControl(canvas, true);
    camera.setPosition(new BABYLON.Vector3(0, 1, -10));
    camera.lowerAlphaLimit = BABYLON.Tools.ToRadians(-140);
    camera.upperAlphaLimit = BABYLON.Tools.ToRadians(-40);
    camera.lowerBetaLimit = Math.PI / 4;
    camera.upperBetaLimit = Math.PI / 2;
    camera.lowerRadiusLimit = 5;
    camera.upperRadiusLimit = 15;

    const loadingScreenDiv = document.getElementById('loadingScreen');

    console.log("Starting to load mesh...");
    BABYLON.SceneLoader.ImportMesh('', './assets/', 'MartinTete2.glb', scene, function (meshes, particleSystems, skeletons, animationGroups) {
        console.log("Mesh loaded.");
        mesh = meshes[0];
        console.log("Mesh found and added to scene.");
        mesh.scaling = new BABYLON.Vector3(10, 10, 10);
        mesh.receiveShadows = true;
        shadowGenerator.addShadowCaster(mesh);
        meshes.forEach((mesh) => {
            if (mesh.name == "Head") {
                headMesh = mesh
            }
        })
        loadingScreenDiv.style.display = 'none';
    }, null, function (scene, event) {
        console.log(`${event.loaded}/${event.total}`);
    });

    return scene;
}

const mouseMove = async (meshs, viseme, start) => {
    console.log(start)
    setTimeout(() => {
        meshs.forEach((mesh) => {
            const morphTargetManager = mesh.morphTargetManager;
            if (morphTargetManager) {
                for (let i = 0; i < morphTargetManager.numTargets; i++) {
                    const target = morphTargetManager.getTarget(i);
                    if (target.name != viseme) {
                        continue;
                    }
                    const influenceAnimation = new BABYLON.Animation(
                        `influenceAnimation_${target.name}`,
                        "influence",
                        60,  // 60 frames per second
                        BABYLON.Animation.ANIMATIONTYPE_FLOAT,
                        BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
                    );
                    const keys = [
                        { frame: 0, value: 0.0 },  // Start at 0 influence
                        { frame: 10, value: 0.7 }, // Peak at 1 influence after half a second
                        { frame: 20, value: 0.0 }  // Back to 0 influence after 1 second
                    ];

                    influenceAnimation.setKeys(keys);
                    target.animations = [];
                    target.animations.push(influenceAnimation);
                    scene.beginAnimation(target, 0, 20, false);
                }
            }
        })
    }, start);
}

scene = createScene();

engine.runRenderLoop(function () {
    scene.render();
});

window.addEventListener('resize', function () {
    engine.resize();
});


let recorder;
let audioBlob;
document.getElementById('call_btn').addEventListener('mousedown', startRecording);
document.getElementById('call_btn').addEventListener('mouseup', stopRecording);

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

const visems = [
    "mouthOpen",
    "viseme_PP",
    "viseme_FF",
    "Viseme_TH",
    "viseme_DD",
    "viseme_kk",
    "viseme_CH",
    "viseme_SS",
    "viseme_nn",
    "viseme_RR",
    "viseme_aa",
    "viseme_E",
    "viseme_I",
    "viseme_O",
    "viseme_U",
]

async function sendAudioToBackend(audioBlob) {
    // Prepare FormData to send the audio blob
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.mp3');

    try {
        const response = await fetch('https://api.digicopy.me/upload', {
            method: 'POST',
            body: formData
        });
        // Expect the response as JSON
        const jsonResponse = await response.json();
        console.log(jsonResponse)
        const transcribedText = jsonResponse.text;
        const audioBase64 = jsonResponse.audio;
        const steps = jsonResponse.steps;
        const audioPlayer = document.getElementById('audio-player');
        if (audioBase64) {
            const audioUrl = `data:audio/mp3;base64,${audioBase64}`;
            audioPlayer.src = audioUrl;
            audioPlayer.play();
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const startTime = step['start'];
                await mouseMove([headMesh], step['viseme'], startTime * 1000);
            }
        } else {
            console.error('No audio data received from backend.');
        }
    } catch (error) {
        console.error('Error sending audio to backend:', error);
    }
}

// const videoInput = document.getElementById('file');

// const transcriptText = document.getElementById("transcriptText");
// uploadButton.addEventListener('click', async () => {
//     const file = videoInput.files[0];

//     if (!file) {
//         console.log('No video file selected');
//         return;
//     }
//     const formData = new FormData();
//     formData.append('video', file, file.name);

//     const response = await fetch('http://localhost:5000/uploadVideo', {
//         method: 'POST',
//         body: formData
//     });
//     const jsonResponse = await response.json();
//     transcriptText.innerText = jsonResponse.text;
// });

// const fileInput = document.getElementById("file");
// const videoPreview = document.getElementById("videoPreview");

// // Event listener for file selection
// fileInput.addEventListener("change", function () {
//     const file = fileInput.files[0];
//     if (file && file.type.startsWith("video/")) {
//         // Create a URL for the selected file and set it as the video source
//         const fileURL = URL.createObjectURL(file);
//         videoPreview.src = fileURL;
//         videoPreview.style.display = "block"; // Make the video visible
//     } else {
//         // Clear the video preview if the selected file is not a video
//         videoPreview.src = "";
//         videoPreview.style.display = "none";
//     }
// });
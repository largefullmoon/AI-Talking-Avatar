import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

const canvas = document.getElementById('renderCanvas');
const engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });

let scene, camera, mesh, animationGroup, isAnimating = false, sound;

const createScene = function() {
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
    BABYLON.SceneLoader.ImportMesh('', './assets/', 'Liz_v08.glb', scene, function (meshes, particleSystems, skeletons, animationGroups) {
        console.log("Mesh loaded.");
        mesh = meshes[0];
        if (mesh) {
            console.log("Mesh found and added to scene.");
            mesh.scaling = new BABYLON.Vector3(10, 10, 10);
            mesh.receiveShadows = true;
            shadowGenerator.addShadowCaster(mesh);
        } else {
            console.error("Mesh not found!");
        }

        setTimeout(() => {
            if (mesh.material && mesh.material.albedoTexture) {
                console.log("Updating texture sampling mode.");
                mesh.material.albedoTexture.updateSamplingMode(1);
            }
        }, 2000);

        animationGroup = animationGroups[0];
        animationGroup.stop();
        animationGroup.onAnimationGroupEndObservable.add(() => {
            if (animationGroup.to === 0) {
                isAnimating = false;
            }
        });

        sound = new BABYLON.Sound("HelloLiz", "./assets/HelloLiz.wav", scene, null, { autoplay: false });

        console.log("Hiding loading screen.");
        loadingScreenDiv.style.display = 'none';
    }, null, function (scene, event) {
        console.log(`${event.loaded}/${event.total}`);
    });

    return scene;
}

console.log("Initializing scene creation.");
scene = createScene();

const animateButton = document.getElementById('animateButton');

animateButton.addEventListener('click', function() {
    if (animationGroup) {
        if (isAnimating) {
            console.log("Stopping animation.");
            animationGroup.stop();
            if (sound) {
                sound.stop();
            }
            isAnimating = false;
        } else {
            console.log("Starting animation.");
            animationGroup.start(false, 1.0, 0, animationGroup.to - 1, false);
            if (sound) {
                sound.play();
            }
            animationGroup.onAnimationGroupEndObservable.addOnce(() => {
                if (sound) {
                    sound.stop();
                }
                isAnimating = false;
            });
            isAnimating = true;
        }
    }
});

engine.runRenderLoop(function() {
    scene.render();
});

window.addEventListener('resize', function() {
    engine.resize();
});

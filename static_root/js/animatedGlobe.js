/* VARIABLES */
let canvas;
let scene;
let renderer;
let data;
let globeElement;

// Cache DOM selectors
const container = document.querySelector('.js-globe');

// Object for country HTML elements and variables
const elements = {};

// Three group objects
const groups = {
    main: null, // A group containing everything
    globe: null, // A group containing the globe sphere (and globe dots)
    globeDots: null, // A group containing the globe dots
};

// Map properties for creation and rendering
const props = {
    mapSize: {
        // Size of the map from the intial source image (on which the dots are positioned on)
        width: 2048 / 2,
        height: 1024 / 2,
    },
    position: {
        x: 350,
        y: 350
    },
    globeRadius: 200, // Radius of the globe (used for many calculations)
    colours: {
        globeDots: '#000', // No need to use the Three constructor as this value is used for the HTML canvas drawing 'fillStyle' property
    }
};

// Angles used for animating the camera
const camera = {
    object: null, // Three object of the camera
    controls: null, // Three object of the orbital controls
    angles: {
        // Object of the camera angles for animating
        current: {
            azimuthal: null,
            polar: null,
        },
        target: {
            azimuthal: null,
            polar: null,
        },
    },
};

// Booleans and values for animations
const animations = {
    finishedIntro: false, // Boolean of when the intro animations have finished
    dots: {
        current: 0, // Animation frames of the globe dots introduction animation
        total: 170, // Total frames (duration) of the globe dots introduction animation,
        points: [], // Array to clone the globe dots coordinates to
    },
    globe: {
        current: 0, // Animation frames of the globe introduction animation
        total: 80, // Total frames (duration) of the globe introduction animation,
    }
};

/* SETUP */

const getData = async () => {
    try {
        const results = await fetch('https://s3-us-west-2.amazonaws.com/s.cdpn.io/617753/globe-points.json');
        data = await results.json();
        return setupScene();
    } catch (error) {
        return alert('Unable to get data');
    }
};

const setupScene = () => {
    canvas = container.querySelector('.js-canvas');

    scene = new THREE.Scene();
    renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true,
        alpha: true,
        shadowMapEnabled: false,
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(3);
    renderer.setClearColor(0x000000, 0);

    // Main group that contains everything
    groups.main = new THREE.Group();
    groups.main.name = 'Main';

    // Add the main group to the scene
    scene.add(groups.main);

    // Render camera and add orbital controls
    addCamera();
    addControls();

    // Render objects
    addGlobe();

    const { azimuthal, polar } = returnCameraAngles(props.position.x, props.position.y);
    camera.angles.target.azimuthal = azimuthal;
    camera.angles.target.polar = polar;

    // Start the requestAnimationFrame loop
    render();
    animate();

    const canvasResizeBehaviour = () => {
        const { innerWidth, innerHeight } = window;
        container.width = innerWidth;
        container.height = innerHeight;
        container.style.width = `${innerWidth}px`;
        container.style.height = `${innerHeight}px`;

        camera.object.aspect = container.offsetWidth / container.offsetHeight;
        camera.object.updateProjectionMatrix();

        renderer.setSize(container.offsetWidth, container.offsetHeight);
    };

    window.addEventListener('resize', canvasResizeBehaviour);
    window.addEventListener('orientationchange', canvasResizeBehaviour);
    canvasResizeBehaviour();
};

/* CAMERA AND CONTROLS */

const addCamera = () => {
    const { clientWidth, clientHeight } = canvas;
    camera.object = new THREE.PerspectiveCamera(60, clientWidth / clientHeight, 1, 10000);
    camera.object.position.z = props.globeRadius * 1.6;
};

const addControls = () => {
    camera.controls = new OrbitControls(camera.object, canvas);
    camera.controls.enableKeys = true;
    camera.controls.enablePan = true;
    camera.controls.enableZoom = true;
    camera.controls.enableDamping = false;
    camera.controls.enableRotate = true;

    // Set the initial camera angles to something crazy for the introduction animation
    camera.angles.current.azimuthal = -Math.PI;
    camera.angles.current.polar = 0;
};

/* RENDERING */

const render = () => renderer.render(scene, camera.object);

const animate = () => {
    requestAnimationFrame(animate);

    if (groups.globeDots) {
        introAnimate();
    }

    camera.controls.update();
    render();
};

/* GLOBE */

const addGlobe = () => {
    const textureLoader = new THREE.TextureLoader();
    textureLoader.setCrossOrigin(true);

    const radius = props.globeRadius - (props.globeRadius * .02);
    const segments = 64;
    const rings = 64;

    // Make gradient
    const canvasSize = 128;
    const textureCanvas = document.createElement('canvas');
    textureCanvas.width = canvasSize;
    textureCanvas.height = canvasSize;
    const canvasContext = textureCanvas.getContext('2d');
    canvasContext.rect(0, 0, canvasSize, canvasSize);
    const canvasGradient = canvasContext.createLinearGradient(0, 0, 0, canvasSize);
    canvasGradient.addColorStop(0, '#f0f0f0');
    canvasGradient.addColorStop(.5, '#f0f0f0');
    canvasGradient.addColorStop(1, '#f0f0f0');
    canvasContext.fillStyle = canvasGradient;
    canvasContext.fill();

    // Make texture
    const texture = new THREE.Texture(textureCanvas);
    texture.needsUpdate = true;

    const geometry = new THREE.SphereGeometry(radius, segments, rings);
    geometry.translate(0, 0, 0);
  
    const material = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        opacity: 0,
    });

    globeElement = new THREE.Mesh(geometry, material);

    groups.globe = new THREE.Group();
    groups.globe.name = 'Globe';

    groups.globe.add(globeElement);
    groups.main.add(groups.globe);

    addGlobeDots();
};

const addGlobeDots = () => {
    const geometry = new THREE.Geometry();

    // Make circle
    const canvasSize = 16;
    const halfSize = canvasSize / 3;
    const textureCanvas = document.createElement('canvas');
    textureCanvas.width = canvasSize;
    textureCanvas.height = canvasSize;
    const canvasContext = textureCanvas.getContext('2d');
    canvasContext.beginPath();
    canvasContext.arc(halfSize, halfSize, halfSize, 0, 2 * Math.PI);
    canvasContext.fillStyle = props.colours.globeDots;
    canvasContext.fill();

    // Make texture
    const texture = new THREE.Texture(textureCanvas);
    texture.needsUpdate = true;

    const material = new THREE.PointsMaterial({
        map: texture,
        size: props.globeRadius / 120,
    });

    const addDot = function({ x, y }) {
        // Add a point with zero coordinates
        const point = new THREE.Vector3(0, 0, 0);
        geometry.vertices.push(point);

        // Add the coordinates to a new array for the intro animation
        const result = returnSphericalCoordinates(x, y);
        animations.dots.points.push(new THREE.Vector3(result.x, result.y, result.z));
    };

    for (let i = 0; i < data.points.length; i++) {
        addDot(data.points[i]);
    }

    // Add the points to the scene
    groups.globeDots = new THREE.Points(geometry, material);
    groups.globe.add(groups.globeDots);
};

/* INTRO ANIMATIONS */

// Easing reference: https://gist.github.com/gre/1650294

const easeInOutCubic = t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;

const introAnimate = () => {
    const { dots, countries } = animations;

    if (dots.current <= dots.total) {
        const points = groups.globeDots.geometry.vertices;
        const totalLength = points.length;

        for (let i = 0; i < totalLength; i++) {
            // Get ease value and add delay based on loop iteration
            let dotProgress = easeInOutCubic(dots.current / dots.total);
            dotProgress = dotProgress + (dotProgress * (i / totalLength));

            if (dotProgress > 1) {
                dotProgress = 1;
            }

            // Move the point
            points[i].x = dots.points[i].x * dotProgress;
            points[i].y = dots.points[i].y * dotProgress;
            points[i].z = dots.points[i].z * dotProgress;

            // Animate the camera at the same rate as the first dot
            if (i === 0) {
                const { current, target } = camera.angles;

                const azimuthalDifference = (current.azimuthal - target.azimuthal) * dotProgress;
                camera.controls.setAzimuthalAngle(current.azimuthal - azimuthalDifference);

                const polarDifference = (current.polar - target.polar) * dotProgress;
                camera.controls.setPolarAngle(current.polar - polarDifference);
            }
        }

        dots.current++;

        // Update verticies
        groups.globeDots.geometry.verticesNeedUpdate = true;
    }

    // Start cycle
    if (!animations.finishedIntro) {
        animations.finishedIntro = true;
        cycleGlobe();
    }
};

const cycleGlobe = () => {
    setInterval(() => {
        // test();
    }, 10)
};

const test = () => {
    props.position.x += 1;

    const { azimuthal, polar } = returnCameraAngles(props.position.x, props.position.y);
    camera.angles.target.azimuthal = azimuthal;

    const azimuthalDifference = (camera.angles.current.azimuthal - camera.angles.target.azimuthal) * 1.1;
    camera.controls.setAzimuthalAngle(camera.angles.current.azimuthal - azimuthalDifference);

    console.log('rotating', props.position, azimuthal, polar)
};

const rotateGlobeToPosition = (x, y, progress = 1) => {
    const { azimuthal, polar } = returnCameraAngles(x, y);
    camera.angles.target.azimuthal = azimuthal;
    camera.angles.target.polar = polar;

    const azimuthalDifference = (camera.angles.current.azimuthal - camera.angles.target.azimuthal) * progress;
    camera.controls.setAzimuthalAngle(camera.angles.current.azimuthal - azimuthalDifference);

    const polarDifference = (camera.angles.current - camera.angles.target.polar) * progress;
    camera.controls.setPolarAngle(camera.angles.current - polarDifference);
};

/* COORDINATE CALCULATIONS */

// Returns an object of 3D spherical coordinates
const returnSphericalCoordinates = (latitude, longitude) => {
    /*
        This function will take a latitude and longitude and calcualte the
        projected 3D coordiantes using Mercator projection relative to the
        radius of the globe.

        Reference: https://stackoverflow.com/a/12734509
    */

    // Convert latitude and longitude on the 90/180 degree axis
    latitude = ((latitude - props.mapSize.width) / props.mapSize.width) * -180;
    longitude = ((longitude - props.mapSize.height) / props.mapSize.height) * -90;

    // Calculate the projected starting point
    const radius = Math.cos(longitude / 180 * Math.PI) * props.globeRadius;
    const x = Math.cos(latitude / 180 * Math.PI) * radius;
    const y = Math.sin(longitude / 180 * Math.PI) * props.globeRadius;
    const z = Math.sin(latitude / 180 * Math.PI) * radius;

    return { x, y, z };
};

// Returns an object of the azimuthal and polar angles of a given map latitude and longitude
const returnCameraAngles = (latitude, longitude) => {
    /*
        This function will convert given latitude and longitude coordinates that are
        proportional to the map dimensions into values relative to PI (which the
        camera uses as angles).

        Note that the azimuthal angle ranges from 0 to PI, whereas the polar angle
        ranges from -PI (negative PI) to PI (positive PI).

        A small offset is added to the azimuthal angle as angling the camera directly on top of a point makes the lines appear flat.
    */

    let azimuthal = ((latitude - props.mapSize.width) / props.mapSize.width) * Math.PI;
    azimuthal = azimuthal + (Math.PI / 2);
    azimuthal = azimuthal + 0.1; // Add a small offset

    let polar = (longitude / (props.mapSize.height * 2)) * Math.PI;

    return { azimuthal, polar };
};

/* INITIALISATION */

if (!window.WebGLRenderingContext) {
    console.warn('WebGL not supported, please use a browser that supports WebGL')
} else {
    getData();
}

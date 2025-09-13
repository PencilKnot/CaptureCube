import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

interface ThreeGLTFViewerProps {
  modelUrl: string;
  className?: string;
}

export function ThreeGLTFViewer({ modelUrl, className = '' }: ThreeGLTFViewerProps) {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    console.log('🚀 Simple GLTF viewer starting for:', modelUrl);

    const container = mountRef.current;
    // Use container's actual dimensions
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Basic Three.js setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.domElement.style.maxWidth = '100%';
    renderer.domElement.style.maxHeight = '100%';
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.display = 'block';
    renderer.domElement.style.objectFit = 'contain';
    container.appendChild(renderer.domElement);

    // Handle resize
    const handleResize = () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;

      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    window.addEventListener('resize', handleResize);

    // Simple lighting
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);

    // Load model
    const loader = new GLTFLoader();
    console.log('📂 Loading model:', modelUrl);

    loader.load(
      modelUrl,
      (gltf) => {
        console.log('✅ Model loaded successfully');
        const model = gltf.scene;

        // Simple scaling
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());

        if (size.length() > 5) {
          const scale = 2 / size.length();
          model.scale.setScalar(scale);
          console.log('🔧 Scaled model by:', scale);
        }

        scene.add(model);
        console.log('🎨 Model added to scene');

        // Render loop - CRITICAL!
        function animate() {
          requestAnimationFrame(animate);
          model.rotation.y += 0.01;
          renderer.render(scene, camera);
        }
        animate();
        console.log('🔄 Animation started');
      },
      undefined, // progress callback
      (error) => {
        console.error('❌ Failed to load model:', error);
      }
    );

    // Cleanup
    return () => {
      console.log('🧹 Cleaning up Three.js scene');
      window.removeEventListener('resize', handleResize);
      if (container && renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [modelUrl]);

  return (
    <div
      ref={mountRef}
      className={`w-full overflow-hidden rounded-lg ${className}`}
      style={{
        background: '#f0f0f0',
        height: 'calc(100vh - 200px)', // Fixed height to prevent overflow
        maxWidth: '100%',
        boxSizing: 'border-box'
      }}
    />
  );
}
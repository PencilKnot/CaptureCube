import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export function TestGLTF({ onBack }: { onBack?: () => void }) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [currentModel, setCurrentModel] = useState('/models/pencil.glb');

  useEffect(() => {
    if (!mountRef.current) return;

    console.log('🚀 Starting simple GLTF test');

    const container = mountRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 600;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xcccccc);

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Light
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);

    // Load GLTF
    const loader = new GLTFLoader();
    console.log('📂 Attempting to load:', currentModel);

    loader.load(
      currentModel,
      (gltf) => {
        console.log('✅ SUCCESS! GLTF loaded:', gltf);
        console.log('📊 Scene children:', gltf.scene.children.length);

        const model = gltf.scene;

        // Get bounding box for debugging
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        console.log('📏 Model size:', size);

        // Scale down if too big
        if (size.length() > 5) {
          const scale = 2 / size.length();
          model.scale.setScalar(scale);
          console.log('🔧 Scaled model by:', scale);
        }

        scene.add(model);
        console.log('🎨 Added model to scene');

        // Simple render loop
        function animate() {
          requestAnimationFrame(animate);
          model.rotation.y += 0.01;
          renderer.render(scene, camera);
        }
        animate();
      },
      (progress) => {
        const percent = (progress.loaded / progress.total) * 100;
        console.log(`📈 Loading: ${percent.toFixed(1)}%`);
      },
      (error) => {
        console.error('💥 FAILED to load GLTF:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error('🔍 Error type:', error?.constructor?.name || 'Unknown');
        console.error('🔍 Error message:', errorMessage);
      }
    );

    // Cleanup
    return () => {
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [currentModel]);

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">GLTF Loading Test</h1>
        {onBack && (
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            ← Back to Main App
          </button>
        )}
      </div>
      <div className="mb-4 p-4 bg-gray-100 rounded">
        <p><strong>Current File:</strong> {currentModel}</p>
        <p><strong>Status:</strong> Check browser console for logs</p>

        <div className="mt-3 flex gap-2">
          <button
            onClick={() => setCurrentModel('/models/pencil.glb')}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              currentModel === '/models/pencil.glb'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            ✏️ Pencil GLB
          </button>
          <button
            onClick={() => setCurrentModel('/models/simple-cube.gltf')}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              currentModel === '/models/simple-cube.gltf'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🟩 Simple Cube
          </button>
          <button
            onClick={() => setCurrentModel('/models/Fox.gltf')}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              currentModel === '/models/Fox.gltf'
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🦊 Fox (Broken)
          </button>
        </div>

        <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
          <p><strong>Testing:</strong> pencil.glb (~19KB) - binary GLB format</p>
          <p>Should load faster than GLTF with external dependencies</p>
        </div>
      </div>
      <div
        ref={mountRef}
        className="w-full h-96 border-2 border-gray-300 bg-gray-50"
        style={{ height: '600px' }}
      />
      <div className="mt-4 text-sm text-gray-600">
        <p>🔍 Open browser console to see detailed loading logs</p>
        <p>If this fails, we'll know it's a GLTF file issue</p>
      </div>
    </div>
  );
}
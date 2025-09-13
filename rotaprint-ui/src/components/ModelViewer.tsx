import { useRef, useEffect } from 'react';

interface ModelViewerProps {
  modelUrl: string;
  className?: string;
}

export function ModelViewer({ modelUrl, className = '' }: ModelViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    // For now, we'll show a placeholder that indicates 3D model support
    // In a real implementation, you'd integrate three.js or model-viewer here
    const placeholder = document.createElement('div');
    placeholder.className = 'w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg border-2 border-dashed border-gray-300';
    placeholder.innerHTML = `
      <div class="text-center p-6">
        <div class="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
          </svg>
        </div>
        <h3 class="text-sm font-medium text-gray-900 mb-2">3D Model Viewer</h3>
        <p class="text-xs text-gray-500">GLB model ready for viewing</p>
        <p class="text-xs text-gray-400 mt-1">${modelUrl}</p>
        <div class="mt-4 flex justify-center space-x-2">
          <button class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors">
            Rotate
          </button>
          <button class="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 transition-colors">
            Zoom
          </button>
          <button class="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors">
            Download
          </button>
        </div>
      </div>
    `;

    viewer.appendChild(placeholder);

    // Cleanup
    return () => {
      if (viewer && placeholder.parentNode) {
        viewer.removeChild(placeholder);
      }
    };
  }, [modelUrl]);

  return (
    <div
      ref={viewerRef}
      className={`min-h-[300px] ${className}`}
      data-model-url={modelUrl}
    />
  );
}

// Modal component for full-screen model viewing
export function ModelViewerModal({
  isOpen,
  onClose,
  modelUrl,
  title
}: {
  isOpen: boolean;
  onClose: () => void;
  modelUrl: string;
  title: string;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl h-[80vh]">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* 3D Viewer */}
          <div className="p-6 h-full">
            <ModelViewer
              modelUrl={modelUrl}
              className="w-full h-full"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
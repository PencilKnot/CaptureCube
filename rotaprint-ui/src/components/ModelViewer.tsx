import { ThreeGLTFViewer } from './ThreeGLBViewer';

interface ModelViewerProps {
  modelUrl: string;
  className?: string;
}

export function ModelViewer({ modelUrl, className = '' }: ModelViewerProps) {
  console.log('🚀 ModelViewer: Simplified - directly rendering ThreeGLTFViewer for:', modelUrl);

  // Simplified: Just render the ThreeGLTFViewer directly
  return <ThreeGLTFViewer modelUrl={modelUrl} className={className} />;
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
import React, { useState } from "react";
import { ModelViewerModal } from "./components/ModelViewer";

export interface ScanData {
  id: string;
  name: string;
  images: File[];
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  model?: {
    url: string;
    description: string;
    measurements?: Record<string, string>;
  };
  createdAt: Date;
}

export interface ScanListing {
  id: string;
  scanId: string;
  title: string;
  description: string;
  modelUrl: string;
  measurements?: Record<string, string>;
  price?: number;
  category: string;
  createdAt: Date;
}

function App() {
  const [scans, setScans] = useState<ScanData[]>([]);
  const [listings, setListings] = useState<ScanListing[]>([]);
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [scanName, setScanName] = useState('');
  const [selectedModel, setSelectedModel] = useState<{ url: string; title: string } | null>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedImages(Array.from(e.target.files));
    }
  };

  const startScan = async () => {
    if (selectedImages.length === 0 || !scanName.trim()) return;

    const newScan: ScanData = {
      id: Date.now().toString(),
      name: scanName.trim(),
      images: selectedImages,
      status: 'uploading',
      progress: 0,
      createdAt: new Date(),
    };

    setScans(prev => [newScan, ...prev]);
    setSelectedImages([]);
    setScanName('');

    // Mock scanning process
    simulateScanProcess(newScan.id);
  };

  const simulateScanProcess = async (scanId: string) => {
    const updateScan = (updates: Partial<ScanData>) => {
      setScans(prev => prev.map(scan =>
        scan.id === scanId ? { ...scan, ...updates } : scan
      ));
    };

    // Simulate upload
    for (let i = 0; i <= 100; i += 20) {
      await new Promise(resolve => setTimeout(resolve, 300));
      updateScan({ progress: i });
    }

    // Start processing
    updateScan({ status: 'processing', progress: 0 });

    // Simulate processing
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 500));
      updateScan({ progress: i });
    }

    // Complete with mock model
    const mockModel = {
      url: '/mock-model.glb',
      description: 'A detailed 3D model of a mechanical component with precise geometric features and surface textures.',
      measurements: {
        'Length': '45.2mm',
        'Width': '23.8mm',
        'Height': '12.1mm',
        'Thread Pitch': '1.25mm',
        'Diameter': '8.5mm'
      }
    };

    updateScan({
      status: 'completed',
      progress: 100,
      model: mockModel
    });

    // Auto-create listing
    const scan = scans.find(s => s.id === scanId);
    const newListing: ScanListing = {
      id: Date.now().toString(),
      scanId: scanId,
      title: `${scan?.name || 'Unnamed Scan'} - 3D Model`,
      description: mockModel.description,
      modelUrl: mockModel.url,
      measurements: mockModel.measurements,
      category: 'Hardware',
      createdAt: new Date(),
    };

    setListings(prev => [newListing, ...prev]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">RotaPrint Scans</h1>
            <div className="flex space-x-4">
              <span className="text-sm text-gray-500">{scans.length} scans</span>
              <span className="text-sm text-gray-500">{listings.length} listings</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Upload Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">New Scan</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scan Name
                  </label>
                  <input
                    type="text"
                    value={scanName}
                    onChange={(e) => setScanName(e.target.value)}
                    placeholder="Enter scan name..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Images
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                      id="image-upload"
                    />
                    <label htmlFor="image-upload" className="cursor-pointer">
                      <div className="space-y-2">
                        <div className="text-gray-400">
                          <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </div>
                        <div className="text-sm text-gray-600">
                          Click to upload images or drag and drop
                        </div>
                      </div>
                    </label>
                  </div>
                </div>

                {selectedImages.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-600 mb-2">
                      {selectedImages.length} images selected
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      {selectedImages.slice(0, 6).map((file, index) => (
                        <div key={index} className="aspect-square bg-gray-100 rounded border overflow-hidden">
                          <img
                            src={URL.createObjectURL(file)}
                            alt={`Preview ${index + 1}`}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ))}
                      {selectedImages.length > 6 && (
                        <div className="aspect-square bg-gray-100 rounded border flex items-center justify-center text-sm text-gray-500">
                          +{selectedImages.length - 6} more
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <button
                  onClick={startScan}
                  disabled={selectedImages.length === 0 || !scanName.trim()}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Start 3D Scan
                </button>
              </div>
            </div>
          </div>

          {/* Scans List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Recent Scans</h2>
              </div>

              <div className="divide-y">
                {scans.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    No scans yet. Upload some images to get started!
                  </div>
                ) : (
                  scans.map((scan) => (
                    <div key={scan.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{scan.name}</h3>
                          <p className="text-sm text-gray-500 mt-1">
                            {scan.images.length} images • {scan.createdAt.toLocaleString()}
                          </p>

                          {/* Status and Progress */}
                          <div className="mt-3">
                            <div className="flex items-center space-x-2">
                              <StatusIcon status={scan.status} />
                              <span className="text-sm capitalize text-gray-700">
                                {scan.status === 'uploading' ? 'Uploading images...' :
                                 scan.status === 'processing' ? 'Generating 3D model...' :
                                 scan.status === 'completed' ? 'Completed' :
                                 'Error'}
                              </span>
                            </div>

                            {(scan.status === 'uploading' || scan.status === 'processing') && (
                              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                <div
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${scan.progress}%` }}
                                />
                              </div>
                            )}
                          </div>

                          {/* Model Info */}
                          {scan.model && (
                            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                              <h4 className="font-medium text-green-900 mb-2">3D Model Ready</h4>
                              <p className="text-sm text-green-700 mb-3">{scan.model.description}</p>

                              {scan.model.measurements && (
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                  {Object.entries(scan.model.measurements).map(([key, value]) => (
                                    <div key={key} className="flex justify-between">
                                      <span className="text-green-600">{key}:</span>
                                      <span className="font-mono text-green-800">{value}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Listings Section */}
            {listings.length > 0 && (
              <div className="mt-8 bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-lg font-semibold text-gray-900">Generated Listings</h2>
                </div>

                <div className="divide-y">
                  {listings.map((listing) => (
                    <div key={listing.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{listing.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{listing.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <span>Category: {listing.category}</span>
                            <span>•</span>
                            <span>{listing.createdAt.toLocaleString()}</span>
                          </div>

                          {listing.measurements && (
                            <div className="mt-3 p-3 bg-gray-50 rounded border">
                              <div className="text-xs font-medium text-gray-700 mb-2">MEASUREMENTS</div>
                              <div className="grid grid-cols-3 gap-2 text-xs">
                                {Object.entries(listing.measurements).map(([key, value]) => (
                                  <div key={key}>
                                    <span className="text-gray-500">{key}</span>
                                    <div className="font-mono text-gray-900">{value}</div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        <button
                          onClick={() => setSelectedModel({ url: listing.modelUrl, title: listing.title })}
                          className="ml-4 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                        >
                          View Model
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Model Viewer Modal */}
      <ModelViewerModal
        isOpen={selectedModel !== null}
        onClose={() => setSelectedModel(null)}
        modelUrl={selectedModel?.url || ''}
        title={selectedModel?.title || ''}
      />
    </div>
  );
}

function StatusIcon({ status }: { status: ScanData['status'] }) {
  switch (status) {
    case 'uploading':
      return <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
    case 'processing':
      return <div className="w-4 h-4 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin" />;
    case 'completed':
      return <div className="w-4 h-4 bg-green-600 rounded-full flex items-center justify-center">
        <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      </div>;
    case 'error':
      return <div className="w-4 h-4 bg-red-600 rounded-full flex items-center justify-center">
        <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </div>;
  }
}

export default App;


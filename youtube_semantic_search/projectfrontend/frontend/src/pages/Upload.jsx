import React, { useState, useRef } from 'react';
import { Button } from '../components/ui/button';
import { Upload as UploadIcon, File, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import api from "../services/api";   // ✅ FastAPI connection

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); 
  const fileInputRef = useRef(null);

  // =============================
  // Handle File Drag + Drop
  // =============================
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    validateFile(selectedFile);
  };

  // Validate CSV file
  const validateFile = (selectedFile) => {
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setUploadStatus(null);
    } else {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a CSV file',
        variant: 'destructive'
      });
    }
  };

  // =============================
  // REAL FastAPI Upload Function
  // =============================
  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploadStatus('processing');

      const formData = new FormData();
      formData.append("file", file);

      // 📌 POST CSV to FastAPI /ingest
      const res = await api.post("/ingest", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      console.log("Server response:", res.data);

      if (res.data.status === "success") {
        setUploadStatus("success");

        toast({
          title: "Upload successful",
          description: `${file.name} has been processed successfully`,
        });

      } else {
        setUploadStatus("error");

        toast({
          title: "Upload failed",
          description: res.data.error || "Backend returned an error",
          variant: "destructive",
        });
      }

    } catch (err) {
      console.error("Upload error:", err);
      setUploadStatus("error");

      toast({
        title: "Upload error",
        description: "Could not connect to backend",
        variant: "destructive",
      });
    }
  };

  // =============================
  // UI Rendering
  // =============================
  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a1128] via-[#1a1f3a] to-[#0a1128] pt-24 pb-16 px-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white mb-3">Upload Dataset</h1>
          <p className="text-gray-400 text-lg">Import your YouTube video dataset for semantic analysis</p>
        </div>

        {/* Upload Area */}
        <div className="mb-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed transition-all duration-300 p-16 text-center ${
              isDragging
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-cyan-500/30 bg-[#1a1f3a]/50 hover:border-cyan-500/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />

            {!file ? (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <div className="p-6 bg-cyan-400/10 rounded-full">
                    <UploadIcon className="w-16 h-16 text-cyan-400" />
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-2xl font-semibold text-white">
                    Drop your YouTube CSV dataset here
                  </p>
                  <p className="text-gray-400">or click the button below to browse files</p>
                </div>

                <Button
                  onClick={handleBrowseClick}
                  className="px-8 py-6 text-lg font-semibold bg-cyan-500 hover:bg-cyan-600 text-white border-0 shadow-lg shadow-cyan-500/30 transition-all duration-300"
                >
                  Browse Files
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <div className="p-6 bg-cyan-400/10 rounded-full">
                    {uploadStatus === 'success' ? (
                      <CheckCircle2 className="w-16 h-16 text-green-400" />
                    ) : uploadStatus === 'error' ? (
                      <AlertCircle className="w-16 h-16 text-red-400" />
                    ) : (
                      <File className="w-16 h-16 text-cyan-400" />
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xl font-semibold text-white">{file.name}</p>
                  <p className="text-gray-400">{(file.size / 1024).toFixed(2)} KB</p>

                  {uploadStatus === 'success' && (
                    <p className="text-green-400 font-medium">Upload successful!</p>
                  )}
                  {uploadStatus === 'processing' && (
                    <p className="text-cyan-400 font-medium">Processing...</p>
                  )}
                </div>

                <div className="flex gap-4 justify-center">
                  {uploadStatus !== 'success' && (
                    <Button
                      onClick={handleUpload}
                      disabled={uploadStatus === 'processing'}
                      className="px-8 py-6 text-lg font-semibold bg-cyan-500 hover:bg-cyan-600 text-white border-0 shadow-lg shadow-cyan-500/30 transition-all duration-300"
                    >
                      {uploadStatus === 'processing' ? 'Processing...' : 'Upload Dataset'}
                    </Button>
                  )}

                  <Button
                    onClick={() => {
                      setFile(null);
                      setUploadStatus(null);
                    }}
                    variant="outline"
                    className="px-8 py-6 text-lg font-semibold bg-transparent border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 hover:border-cyan-400 transition-all duration-300"
                  >
                    Clear
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* CSV Format Info */}
        <div className="bg-[#1a1f3a] border border-cyan-500/20 p-8">
          <h3 className="text-xl font-semibold text-white mb-4">Required CSV Format</h3>
          <p className="text-gray-400 mb-4">Your CSV file should contain the following columns:</p>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-[#0a1128] border border-cyan-500/10">
              <code className="text-cyan-400 font-mono text-sm">video_id</code>
              <p className="text-gray-500 text-xs mt-1">YouTube video identifier</p>
            </div>

            <div className="p-4 bg-[#0a1128] border border-cyan-500/10">
              <code className="text-cyan-400 font-mono text-sm">title</code>
              <p className="text-gray-500 text-xs mt-1">Video title</p>
            </div>

            <div className="p-4 bg-[#0a1128] border border-cyan-500/10">
              <code className="text-cyan-400 font-mono text-sm">channel</code>
              <p className="text-gray-500 text-xs mt-1">Channel name</p>
            </div>

            <div className="p-4 bg-[#0a1128] border border-cyan-500/10">
              <code className="text-cyan-400 font-mono text-sm">description</code>
              <p className="text-gray-500 text-xs mt-1">Video description (optional)</p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-cyan-400/5 border border-cyan-400/20">
            <p className="text-sm text-gray-400">
              <span className="font-semibold text-cyan-400">Note:</span> Files are processed and indexed for semantic search. The system will extract embeddings and store them for fast retrieval.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;

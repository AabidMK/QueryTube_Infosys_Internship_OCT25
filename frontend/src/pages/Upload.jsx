import React, { useState, useRef } from 'react';
import { Button } from '../components/ui/button';
import { Upload as UploadIcon, File, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import api from "../services/api";

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); 
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const handleFileSelect = (e) => validateFile(e.target.files[0]);

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

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploadStatus('processing');

      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post("/ingest", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

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
      setUploadStatus("error");
      toast({
        title: "Upload error",
        description: "Could not connect to backend",
        variant: "destructive",
      });
    }
  };

  const handleBrowseClick = () => fileInputRef.current?.click();

  return (
    <div
      className="min-h-screen pt-24 pb-16 px-6"
      style={{
        background: "#0A0A0A",       // ✔ PURE BLACK BACKGROUND
      }}
    >
      <div className="max-w-4xl mx-auto">

        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white mb-3">Upload Dataset</h1>
          <p className="text-gray-400 text-lg">Import your YouTube video dataset for semantic analysis</p>
        </div>

        {/* Upload Box */}
        <div className="mb-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${isDragging ? "#FFD879" : "rgba(255, 216, 121, 0.3)"}`,  // ✔ GOLD BORDER
              background: isDragging
                ? "rgba(255, 216, 121, 0.05)"
                : "rgba(17, 17, 17, 0.8)",             // ✔ BLACK PANEL BACKGROUND
              transition: "0.3s",
              padding: "60px",
              textAlign: "center",
              borderRadius: "12px"
            }}
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
                <UploadIcon size={60} color="#FFD879" />

                <p className="text-2xl font-semibold text-white">
                  Drop your YouTube CSV dataset here
                </p>
                <p className="text-gray-400">or click the button below to browse files</p>

                <Button
                  onClick={handleBrowseClick}
                  className="px-8 py-6 text-lg font-semibold"
                  style={{
                    background: "linear-gradient(135deg, #FFD879, #FFB85C)", // ✔ GOLD BUTTON
                    color: "#0A0A0A",
                    border: "none"
                  }}
                >
                  Browse Files
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {uploadStatus === "success" ? (
                  <CheckCircle2 size={50} color="#00C851" />
                ) : uploadStatus === "error" ? (
                  <AlertCircle size={50} color="#FF4444" />
                ) : (
                  <File size={50} color="#FFD879" />
                )}

                <p className="text-xl font-semibold text-white">{file.name}</p>

                <div className="flex gap-4 justify-center">
                  {uploadStatus !== "success" && (
                    <Button
                      onClick={handleUpload}
                      className="px-8 py-6 text-lg font-semibold"
                      style={{
                        background: "linear-gradient(135deg, #FFD879, #FFB85C)",
                        color: "#0A0A0A"
                      }}
                    >
                      {uploadStatus === "processing" ? "Processing..." : "Upload Dataset"}
                    </Button>
                  )}

                  <Button
                    onClick={() => {
                      setFile(null);
                      setUploadStatus(null);
                    }}
                    className="px-8 py-6 text-lg font-semibold"
                    style={{
                      background: "transparent",
                      border: "2px solid #FFD879",
                      color: "#FFD879"
                    }}
                  >
                    Clear
                  </Button>
                </div>
              </div>
            )}

          </div>
        </div>

        {/* CSV Format Info */}
        <div
          style={{
            background: "rgba(17,17,17,0.8)",
            border: "1px solid rgba(255,216,121,0.3)",
            padding: "32px"
          }}
        >
          <h3 className="text-xl font-semibold text-white mb-4">Required CSV Format</h3>

          <p className="text-gray-400 mb-4">Your CSV file must contain:</p>

          <div className="grid grid-cols-2 gap-4">
            {["video_id", "title", "channel", "description"].map((col) => (
              <div
                key={col}
                style={{
                  background: "#0A0A0A",
                  border: "1px solid rgba(255,216,121,0.2)",
                  padding: "16px"
                }}
              >
                <code className="text-[#FFD879]">{col}</code>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Upload;

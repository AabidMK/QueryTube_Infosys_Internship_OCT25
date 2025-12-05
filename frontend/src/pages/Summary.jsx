import React, { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { FileText } from "lucide-react";
import api from "../services/api";
import { useLocation } from "react-router-dom";

const Summary = () => {
  const [videoId, setVideoId] = useState("");
  const [summary, setSummary] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const location = useLocation();

  // Load videoId from URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const id = params.get("videoId");

    if (id) {
      setVideoId(id);
      handleGenerate(id);
    }
  }, [location]);

  // Call FastAPI backend
  const handleGenerate = async (id = videoId) => {
    if (!id.trim()) return;

    setIsGenerating(true);
    setSummary(null);

    try {
      const res = await api.get(`/summarize/${id}`);
      if (res.data && !res.data.error) {
        setSummary(res.data);
      }
    } catch (e) {
      console.error("Summary API error:", e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleGenerate();
  };

  return (
    <div className="min-h-screen bg-black pt-24 pb-16 px-6">
      <div className="max-w-5xl mx-auto">

        {/* HEADER */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white mb-3">Video Summary Generator</h1>
          <p className="text-gray-400 text-lg">Get AI-powered summaries of any YouTube video</p>
        </div>

        {/* INPUT */}
        <div className="mb-12">
          <div className="max-w-2xl mx-auto">
            <div className="flex gap-4">

              <Input
                placeholder="Enter YouTube Video ID"
                value={videoId}
                onChange={(e) => setVideoId(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full px-6 py-6 text-lg bg-black 
                           border border-[#FFD87970] 
                           text-white placeholder:text-gray-500
                           focus:border-[#FFD879] focus:shadow-[0_0_10px_#FFD87950]"
              />

              <Button
                onClick={() => handleGenerate()}
                disabled={isGenerating}
                className="px-8 py-6 text-lg font-semibold 
                           bg-[#FFD879] text-black 
                           hover:bg-[#e8c162]"
              >
                {isGenerating ? "Generating..." : "Generate Summary"}
              </Button>

            </div>
          </div>
        </div>

        {/* SUMMARY BOX */}
        {summary && (
          <div className="bg-black 
                          border border-[#FFD87940] 
                          p-10 space-y-10 rounded-xl">

            {/* TITLE */}
            <div>
              <p className="text-[#FFD879] text-lg font-semibold">Title :</p>
              <h2 className="text-3xl font-bold text-white mt-2">{summary.title}</h2>
            </div>

            {/* CHANNEL */}
            <div>
              <p className="text-[#FFD879] text-lg font-semibold">Channel :</p>
              <p className="text-gray-300 text-xl mt-2">{summary.channel}</p>
            </div>

            {/* SUMMARY POINTS */}
            <div>
              <p className="text-[#FFD879] text-lg font-semibold mb-4">Summary :</p>

              <div className="space-y-6">
                {summary.summary_points.map((point, index) => (
                  <div key={index} className="flex gap-4">

                    <div className="w-8 h-8 bg-black 
                                    border border-[#FFD87970] 
                                    text-[#FFD879] font-semibold 
                                    flex items-center justify-center rounded">
                      {index + 1}
                    </div>

                    <p className="flex-1 text-gray-300 leading-relaxed pt-1">
                      {point}
                    </p>

                  </div>
                ))}
              </div>
            </div>

            {/* RESET BUTTON */}
            <div className="flex justify-center">
              <Button
                onClick={() => {
                  setSummary(null);
                  setVideoId("");
                }}
                variant="outline"
                className="px-8 py-4 bg-transparent 
                           border-2 border-[#FFD87970] 
                           text-[#FFD879] 
                           hover:bg-[#FFD87920]"
              >
                Generate Another
              </Button>
            </div>

          </div>
        )}

        {/* EMPTY STATE */}
        {!summary && !isGenerating && (
          <div className="text-center py-20">
            <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Enter a video ID to generate summary</p>
          </div>
        )}

      </div>
    </div>
  );
};

export default Summary;

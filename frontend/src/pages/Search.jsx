import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Search as SearchIcon } from 'lucide-react';
import api from "../services/api";
import { useNavigate } from 'react-router-dom';

const Search = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();

  // Call backend API
  const runSearch = async (query) => {
    try {
      const res = await api.get("/search", { params: { query } });
      return res.data.results || [];
    } catch (err) {
      console.error("Search error:", err);
      return [];
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);

    const data = await runSearch(searchQuery);
    setResults(data);

    setIsSearching(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleSummarize = (videoId) => {
    navigate(`/summary?videoId=${videoId}`);
  };

  return (
    <div className="min-h-screen bg-black pt-24 pb-16 px-6">
      <div className="max-w-6xl mx-auto">

        {/* HEADER */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-3">Semantic Video Search</h1>
          <p className="text-gray-400 text-lg">
            Discover videos through intelligent content understanding
          </p>
        </div>

        {/* SEARCH BAR */}
        <div className="mb-12">
          <div className="flex gap-4">

            {/* Input */}
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />

              <Input
                placeholder="Search videos semantically…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full pl-12 pr-4 py-6 text-lg
                           bg-black border border-[#FFD87970]
                           text-white placeholder:text-gray-500
                           focus:border-[#FFD879] focus:shadow-[0_0_10px_#FFD87950]"
              />
            </div>

            {/* Button */}
            <Button
              onClick={handleSearch}
              disabled={isSearching}
              className="px-8 py-6 text-lg font-semibold 
                         bg-[#FFD879] text-black
                         hover:bg-[#e8c162] transition shadow-lg"
            >
              {isSearching ? "Searching..." : "Search"}
            </Button>
          </div>
        </div>

        {/* RESULTS */}
        {results.length > 0 && (
          <div className="space-y-8">

            {results.map((video, index) => (
              <div
                key={video.id || index}
                className="p-6 bg-black 
                           border border-[#FFD87940]
                           hover:border-[#FFD879] 
                           rounded-xl transition-all"
              >
                <div className="flex gap-6">

                  {/* Thumbnail */}
                  <div className="w-64 h-40 bg-gray-900 overflow-hidden rounded-md border border-[#FFD87930]">
                    <img
                      src={`https://img.youtube.com/vi/${video.id}/hqdefault.jpg`}
                      alt={video.title}
                      className="w-full h-full object-cover hover:scale-105 transition-transform"
                    />
                  </div>

                  {/* DETAILS */}
                  <div className="flex-1 space-y-3">
                    <h2 className="text-2xl font-bold text-white">{video.title}</h2>

                    <p className="text-gray-400">
                      📺 {video.channel_title || "Unknown Channel"}
                    </p>

                    <div className="grid grid-cols-2 gap-4 text-gray-300 text-sm mt-3">

                      <p>
                        <span className="font-semibold text-[#FFD879]">Video ID:</span>
                        <span className="ml-2 px-2 py-1 bg-gray-800 rounded text-white">{video.id}</span>
                      </p>

                      <p>👁️ <span className="font-semibold text-[#FFD879]">Views:</span> {video.viewCount}</p>

                      <p>👍 <span className="font-semibold text-[#FFD879]">Likes:</span> {video.likes || 0}</p>

                      <p>✨ <span className="font-semibold text-[#FFD879]">Similarity:</span> 
                        {video.similarity ? video.similarity.toFixed(3) : "0.00"}
                      </p>

                    </div>

                    {/* BUTTONS */}
                    <div className="flex gap-4 mt-5">

                      <Button
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${video.id}`, "_blank")}
                        className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white"
                      >
                        ▶️ Watch on YouTube
                      </Button>

                      <Button
                        onClick={() => handleSummarize(video.id)}
                        className="px-6 py-3 bg-[#FFD879] hover:bg-[#e8c162] text-black"
                      >
                        📄 Summary
                      </Button>

                    </div>

                  </div>

                </div>
              </div>
            ))}

          </div>
        )}

        {/* EMPTY STATE */}
        {results.length === 0 && !isSearching && (
          <div className="text-center py-20">
            <SearchIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Enter a search query to find videos</p>
          </div>
        )}

      </div>
    </div>
  );
};

export default Search;

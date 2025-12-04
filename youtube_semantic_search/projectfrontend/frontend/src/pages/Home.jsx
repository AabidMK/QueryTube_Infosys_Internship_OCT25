import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Search, Upload } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full overflow-hidden">

      {/* Background Image */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage:
            "url('https://customer-assets.emergentagent.com/job_09d2c2bc-46de-4f9e-bfa8-592bd5e5a878/artifacts/7zgii2z0_bg%20image.png')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      />

      {/* Soft Overlay (lighter than before so image is visible) */}
      <div className="absolute inset-0 bg-[#0a1128]/60 backdrop-blur-sm z-10"></div>

      {/* Content */}
      <div className="relative z-20 flex items-center justify-center min-h-screen px-6">
        <div className="max-w-5xl mx-auto text-center space-y-10">

          {/* Hero Title */}
          <h1 className="text-4xl md:text-7xl font-extrabold text-white leading-tight drop-shadow-xl">
            Discover Smarter
            <span className="block mt-3 bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
              YouTube Search with AI
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-200 max-w-3xl mx-auto leading-relaxed">
            A semantic search engine that understands YouTube videos 
            beyond keywords - powered by transformers, NLP, and intelligent embeddings.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mt-8">
            <Button
              onClick={() => navigate('/search')}
              className="px-8 py-6 text-lg font-semibold bg-cyan-500 hover:bg-cyan-600 text-white border-0 shadow-lg shadow-cyan-500/30 transition-all duration-300 hover:shadow-xl hover:scale-105"
            >
              <Search className="w-5 h-5 mr-2" />
              Start Search
            </Button>

            <Button
              onClick={() => navigate('/upload')}
              variant="outline"
              className="px-8 py-6 text-lg font-semibold border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400/10 hover:border-cyan-400 transition-all duration-300 hover:scale-105"
            >
              <Upload className="w-5 h-5 mr-2" />
              Upload Dataset
            </Button>
          </div>

          {/* Project Description Section */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-white/10 backdrop-blur-md rounded-xl border border-cyan-500/20 shadow-lg">
              <h3 className="text-cyan-300 font-bold text-2xl mb-2">Semantic Intelligence</h3>
              <p className="text-gray-200 text-sm">
                Uses transformer-based embeddings to understand video meaning,
                not just keywords. 
              </p>
            </div>

            <div className="p-6 bg-white/10 backdrop-blur-md rounded-xl border border-cyan-500/20 shadow-lg">
              <h3 className="text-cyan-300 font-bold text-2xl mb-2">AI-Based Similarity Search</h3>
              <p className="text-gray-200 text-sm">
                Retrieves top-5 relevant videos using similarity metrics.
              </p>
            </div>

            <div className="p-6 bg-white/10 backdrop-blur-md rounded-xl border border-cyan-500/20 shadow-lg">
              <h3 className="text-cyan-300 font-bold text-2xl mb-2">End-to-End Pipeline</h3>
              <p className="text-gray-200 text-sm">
                Includes data extraction, cleaning, embeddings, ranking, and a complete search UI.
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};

export default Home;

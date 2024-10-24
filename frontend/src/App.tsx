import React, { useState, useEffect } from "react";
import { ServerHealth } from "./components/ServerHealth";
import { UploadSection } from "./components/UploadSection";
import { SearchSection } from "./components/SearchSection";
import { useDebounce } from "./hooks/useDebounce";

const API_URL = import.meta.env.VITE_APP_BACKEND_ADDRESS;

interface SearchResult {
  id: number;
  fileName: string;
  content: string;
  timestamp: string;
  highlights: Array<{
    start: number;
    end: number;
    text: string;
  }>;
}

const App: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [serverHealth, setServerHealth] = useState("Healthy");
  const [transcriptionStatus, setTranscriptionStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        setServerHealth(data.status);
      } catch (error) {
        setServerHealth("Unhealthy");
      }
    };

    checkServerHealth();
    const interval = setInterval(checkServerHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const performSearch = async () => {
      if (!debouncedSearchTerm.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const response = await fetch(
          `${API_URL}/search?q=${encodeURIComponent(debouncedSearchTerm)}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Transform the data to match the SearchResult interface
        const transformedResults = data.map((result: any) => ({
          id: result.id,
          fileName: result.file_name,
          content: result.transcription,
          timestamp: new Date().toISOString(), // Add proper timestamp if available
          highlights: result.highlights,
        }));

        setSearchResults(transformedResults);
      } catch (error) {
        console.error("Search failed:", error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    performSearch();
  }, [debouncedSearchTerm]);
  const handleSearchChange = (term: string) => {
    // Prevent default form submission behavior
    setSearchTerm(term);
  };
  const handleTranscribe = async () => {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("upload_files", file);
    });

    try {
      const response = await fetch(`${API_URL}/transcribe`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setTranscriptionStatus("success");
      } else {
        setTranscriptionStatus("error");
      }
    } catch (error) {
      setTranscriptionStatus("error");
    }
  };

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-4 text-center">
          Audio Transcription App
        </h1>
        <ServerHealth status={serverHealth} />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <UploadSection
            selectedFiles={selectedFiles}
            onFilesSelect={setSelectedFiles}
            onTranscribe={handleTranscribe}
            transcriptionStatus={transcriptionStatus}
          />

          <SearchSection
            searchTerm={searchTerm}
            onSearchTermChange={handleSearchChange}
            searchResults={searchResults}
            isSearching={isSearching}
          />
        </div>
      </div>
    </div>
  );
};

export default App;

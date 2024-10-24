import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { HighlightText } from "./HighlightText";

interface Highlight {
  start: number;
  end: number;
  text: string;
}

interface SearchResult {
  id: number;
  fileName: string;
  content: string;
  timestamp: string;
  highlights: Highlight[];
}

interface SearchSectionProps {
  searchTerm: string;
  onSearchTermChange: (term: string) => void;
  searchResults: SearchResult[];
  isSearching: boolean;
}

export const SearchSection: React.FC<SearchSectionProps> = ({
  searchTerm,
  onSearchTermChange,
  searchResults,
  isSearching,
}) => {
  return (
    <Card className="bg-white/10 border-0">
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          Transcription Search
        </h2>

        <div className="space-y-4">
          <div className="relative">
            <Input
              placeholder="Search Text"
              value={searchTerm}
              onChange={(e) => onSearchTermChange(e.target.value)}
              className="bg-white/5 border-0 text-white pr-10"
            />
            {isSearching && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <Loader2 className="h-4 w-4 animate-spin text-white/70" />
              </div>
            )}
          </div>

          <div className="min-h-[200px] bg-white/5 rounded-lg p-4 space-y-4 overflow-y-auto max-h-[400px]">
            {searchResults.map((result, index) => (
              <div
                key={index}
                className="text-white/90 bg-white/5 p-3 rounded-lg space-y-2"
              >
                <div className="font-medium text-sm text-white/70">
                  {result.fileName}
                </div>
                <div className="text-sm">
                  <HighlightText
                    text={result.content}
                    highlight={searchTerm}
                    highlights={result.highlights}
                  />
                </div>
                <div className="text-xs text-white/50">{result.timestamp}</div>
              </div>
            ))}

            {!isSearching && searchResults.length === 0 && searchTerm && (
              <div className="text-white/50 text-center py-8">
                No results found for "{searchTerm}"
              </div>
            )}

            {!searchTerm && (
              <div className="text-white/50 text-center py-8">
                Start typing to search transcriptions
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

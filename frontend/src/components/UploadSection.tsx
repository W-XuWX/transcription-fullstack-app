import React, { useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, AlertCircle } from "lucide-react";

interface UploadSectionProps {
  selectedFiles: File[];
  onFilesSelect: (files: File[]) => void;
  onTranscribe: () => void;
  transcriptionStatus: "idle" | "success" | "error";
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  selectedFiles,
  onFilesSelect,
  onTranscribe,
  transcriptionStatus,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      onFilesSelect(Array.from(event.target.files));
    }
  };

  return (
    <Card className="bg-white/10 border-0 h-full">
      <CardContent className="p-6 h-full flex flex-col">
        <h2 className="text-xl font-semibold text-white mb-4">
          Upload Audio Files
        </h2>

        <div className="flex flex-col h-full gap-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="audio/*"
            multiple
            className="hidden"
          />

          <div className="flex gap-2">
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1"
              variant="secondary"
            >
              Upload files
            </Button>

            <Button
              onClick={onTranscribe}
              className="flex-1"
              disabled={selectedFiles.length === 0}
            >
              Transcribe
            </Button>
          </div>

          <div className="flex-1 bg-white/5 rounded-lg p-4 overflow-y-auto">
            {selectedFiles.map((file) => (
              <div key={file.name} className="text-white">
                {file.name}
              </div>
            ))}
          </div>

          {transcriptionStatus !== "idle" && (
            <div className="flex items-center gap-2 text-white">
              Transcription:{" "}
              {transcriptionStatus === "success" ? (
                <span className="text-green-500 flex items-center gap-1">
                  Success <Check size={16} />
                </span>
              ) : (
                <span className="text-red-500 flex items-center gap-1">
                  Error <AlertCircle size={16} />
                </span>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

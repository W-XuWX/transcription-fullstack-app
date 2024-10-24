import React from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface ServerHealthProps {
  status: string;
}

export const ServerHealth: React.FC<ServerHealthProps> = ({ status }) => {
  return (
    <div className="flex justify-center mb-6">
      <Alert
        variant={status === "Healthy" ? "default" : "destructive"}
        className="w-auto bg-transparent border-none"
      >
        <AlertDescription className="flex items-center gap-2 bg-transparent">
          <span style={{ color: "white" }}>Server health: </span>{" "}
          <span
            className={status === "Healthy" ? "text-green-500" : "text-red-500"}
          >
            {status}
          </span>
        </AlertDescription>
      </Alert>
    </div>
  );
};

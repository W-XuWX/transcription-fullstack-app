import React from "react";

interface Highlight {
  start: number;
  end: number;
  text: string;
}

interface HighlightTextProps {
  text: string;
  highlight: string;
  highlights?: Highlight[]; // Optional server-side highlights
}

export const HighlightText: React.FC<HighlightTextProps> = ({
  text,
  highlight,
  highlights,
}) => {
  // If no highlight term is provided, return plain text
  if (!highlight.trim() && (!highlights || highlights.length === 0)) {
    return <span>{text}</span>;
  }

  // If we have server-side highlights, use those
  if (highlights && highlights.length > 0) {
    const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);
    const result: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedHighlights.forEach((highlight, index) => {
      // Add text before the highlight
      if (highlight.start > lastIndex) {
        result.push(
          <span key={`text-${index}`}>
            {text.slice(lastIndex, highlight.start)}
          </span>
        );
      }

      // Add highlighted text
      result.push(
        <span
          key={`highlight-${index}`}
          className="bg-yellow-500/50 text-white font-medium"
        >
          {text.slice(highlight.start, highlight.end)}
        </span>
      );

      lastIndex = highlight.end;
    });

    // Add any remaining text
    if (lastIndex < text.length) {
      result.push(<span key="text-end">{text.slice(lastIndex)}</span>);
    }

    return <span>{result}</span>;
  }

  // Fallback to original client-side highlighting
  const regex = new RegExp(`(${highlight})`, "gi");
  const parts = text.split(regex);

  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <span key={i} className="bg-yellow-500/50 text-white font-medium">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
};

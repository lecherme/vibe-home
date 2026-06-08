"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Loader2 } from "lucide-react";

interface AiSearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function AiSearchBar({ onSearch, isLoading }: AiSearchBarProps) {
  const [query, setQuery] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="flex w-full items-center space-x-2">
      <Input
        type="text"
        placeholder="Try 'a 3 bedroom house under $500k in Seattle'"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        className="flex-1"
      />
      <Button
        type="button"
        disabled={isLoading || !query.trim()}
        onClick={() => {
          if (query.trim() && !isLoading) {
            onSearch(query.trim());
          }
        }}
        className="bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {isLoading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Search className="mr-2 h-4 w-4" />
        )}
        AI Search
      </Button>
    </div>
  );
}

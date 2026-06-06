"use client";

import { FormEvent, KeyboardEvent, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type PaginationControlsProps = {
  page: number;
  totalPages: number;
  onPageChange: (newPage: number) => void;
  isLoading?: boolean;
  className?: string;
};

export function PaginationControls({
  page,
  totalPages,
  onPageChange,
  isLoading = false,
  className = "",
}: PaginationControlsProps) {
  const [pageInput, setPageInput] = useState(String(page));

  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  if (totalPages <= 1) {
    return null;
  }

  const clampPage = (value: number) => Math.min(Math.max(value, 1), totalPages);

  const goToPage = () => {
    const parsedPage = Number(pageInput);
    const nextPage = Number.isFinite(parsedPage) ? clampPage(Math.trunc(parsedPage)) : page;

    setPageInput(String(nextPage));
    onPageChange(nextPage);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    goToPage();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      goToPage();
    }
  };

  return (
    <div className={`flex flex-wrap justify-center items-center gap-4 ${className}`}>
      <Button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1 || isLoading}
        className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
      >
        Previous
      </Button>
      <span className="text-sm text-slate-700">
        Page {page} of {totalPages}
      </span>
      <Button
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages || isLoading}
        className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
      >
        Next
      </Button>
      <form onSubmit={handleSubmit} noValidate className="flex items-center gap-2">
        <Label htmlFor="go-to-page" className="sr-only">
          Go to page
        </Label>
        <Input
          id="go-to-page"
          type="number"
          value={pageInput}
          onChange={(event) => setPageInput(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          className="w-20 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
        />
        <Button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
        >
          Go
        </Button>
      </form>
    </div>
  );
}

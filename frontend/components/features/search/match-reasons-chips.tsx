import type { MatchReason } from "@/types/ai-search";

interface MatchReasonsChipsProps {
  reasons?: MatchReason[];
}

export function MatchReasonsChips({ reasons }: MatchReasonsChipsProps) {
  if (!reasons || reasons.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2 px-1">
      {reasons.map((reason) => {
        const stateLabel = reason.matched ? reason.label : `△ ${reason.label}`;
        const className = !reason.matched
          ? "border-amber-200 bg-amber-50 text-amber-700"
          : reason.strength === "hard"
            ? "border-slate-200 bg-slate-100 text-slate-700"
            : "border-emerald-200 bg-emerald-50 text-emerald-700";

        return (
          <span
            key={`${reason.field}-${reason.label}`}
            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${className}`}
          >
            {stateLabel}
          </span>
        );
      })}
    </div>
  );
}

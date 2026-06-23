import React from "react";
import type { IntentField, InterpretedNeeds } from "@/types/ai-search";

interface InterpretedNeedsCardProps {
  interpretedNeeds?: InterpretedNeeds;
  interpretedIntent?: IntentField[];
}

export function InterpretedNeedsCard({
  interpretedNeeds,
  interpretedIntent,
}: InterpretedNeedsCardProps) {
  const hasNeeds = !!interpretedNeeds?.needs && interpretedNeeds.needs.length > 0;
  const hasNotices = !!interpretedNeeds?.notices && interpretedNeeds.notices.length > 0;
  const hasUnresolved = !!interpretedNeeds?.unresolved && interpretedNeeds.unresolved.length > 0;
  const hasNonFilterableIntent = !!interpretedIntent && interpretedIntent.some(i => !i.filterable);

  const isEmpty = !hasNeeds && !hasNotices && !hasUnresolved && !hasNonFilterableIntent;

  if (isEmpty) {
    return null;
  }

  return (
    <div className="mt-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all hover:shadow-md duration-300 space-y-4">
      {/* Notices section */}
      {hasNotices && (
        <div className="flex flex-wrap gap-2">
          {interpretedNeeds.notices.map((notice, idx) => {
            const isTension = notice.type === "tension";
            const bgClass = isTension
              ? "bg-amber-50 border-amber-200 text-amber-600"
              : "bg-blue-50 border-blue-200 text-blue-800";
            const icon = isTension ? "⚠️" : "💡";

            return (
              <div
                key={idx}
                className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium shadow-sm transition-transform hover:scale-[1.01] ${bgClass}`}
              >
                <span className="flex-shrink-0" aria-hidden="true">
                  {icon}
                </span>
                <span>{notice.message}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Needs & Intent section */}
      {(hasNeeds || hasNonFilterableIntent) && (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2.5 pt-1 border-t border-gray-100">
          {hasNeeds && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Understood Needs:</span>
              {interpretedNeeds.needs.map((need, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center rounded-md border border-gray-200 bg-gray-50 px-2.5 py-0.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100"
                >
                  {need.raw}
                </span>
              ))}
            </div>
          )}

          {hasNonFilterableIntent && (
            <div className="flex flex-wrap items-center gap-2">
              {hasNeeds && <span className="h-4 w-px bg-gray-200 hidden sm:inline" />}
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Additional Intent:</span>
              {interpretedIntent
                .filter((intent) => !intent.filterable)
                .map((intent, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center rounded-md border border-dashed border-gray-300 bg-gray-50/50 px-2.5 py-0.5 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-50"
                  >
                    {intent.label}（暂无数据）
                  </span>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Unresolved section */}
      {hasUnresolved && (
        <div className="text-xs text-gray-400 italic pt-1 border-t border-gray-50">
          以下内容暂未用于筛选：{interpretedNeeds.unresolved.join("、")}
        </div>
      )}
    </div>
  );
}

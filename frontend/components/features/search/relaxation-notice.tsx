import type { RelaxationRecord } from "@/types/ai-search";

interface RelaxationNoticeProps {
  relaxations?: RelaxationRecord[];
}

const FIELD_LABELS: Record<string, string> = {
  subway_distance_max: "地铁距离限制",
  built_year_min: "楼龄限制",
  location: "区域限制",
};

function formatValue(value: unknown) {
  if (value == null) {
    return "已移除";
  }

  return String(value);
}

function describeRelaxation(relaxation: RelaxationRecord) {
  const label = FIELD_LABELS[relaxation.field] ?? relaxation.field;

  if (relaxation.to_value == null) {
    return `${label}已移除`;
  }

  return `${label}已从 ${formatValue(relaxation.from_value)} 放宽到 ${formatValue(relaxation.to_value)}`;
}

export function RelaxationNotice({ relaxations }: RelaxationNoticeProps) {
  if (!relaxations || relaxations.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      已放宽：{relaxations.map(describeRelaxation).join("，")}
    </div>
  );
}

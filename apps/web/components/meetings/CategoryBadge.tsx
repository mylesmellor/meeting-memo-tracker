import { Badge } from "@/components/ui/badge";

const categoryConfig = {
  work: { label: "Work", variant: "blue" as const },
  home: { label: "Home", variant: "green" as const },
  private: { label: "Private", variant: "purple" as const },
};

export function CategoryBadge({ category }: { category: string }) {
  const config = categoryConfig[category as keyof typeof categoryConfig] ?? {
    label: category,
    variant: "secondary" as const,
  };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

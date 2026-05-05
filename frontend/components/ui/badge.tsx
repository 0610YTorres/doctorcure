import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "info";
}

const variantClasses: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default: "bg-gray-100 text-gray-700",
  success: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  error:   "bg-red-100 text-red-700",
  info:    "bg-brand-50 text-brand-600",
};

export function Badge({ variant = "default", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

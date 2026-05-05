import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:  "bg-brand-500 text-white hover:bg-brand-600 shadow-sm",
        outline:  "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50",
        ghost:    "text-gray-600 hover:bg-gray-100",
        danger:   "bg-red-600 text-white hover:bg-red-700",
        success:  "bg-emerald-600 text-white hover:bg-emerald-700",
      },
      size: {
        sm:  "h-8 px-3 text-xs",
        md:  "h-10 px-4",
        lg:  "h-12 px-6 text-base",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  }
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = "Button";

export { Button, buttonVariants };

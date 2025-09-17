import { clsx } from "clsx";
import type { ButtonHTMLAttributes, DetailedHTMLProps } from "react";

const base = "inline-flex items-center justify-center rounded-md border border-slate-600 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50";

export type ButtonProps = DetailedHTMLProps<
  ButtonHTMLAttributes<HTMLButtonElement>,
  HTMLButtonElement
> & {
  variant?: "default" | "outline";
};

export function Button({ variant = "default", className, ...props }: ButtonProps) {
  const variantClass =
    variant === "outline"
      ? "border-slate-500 bg-transparent hover:bg-slate-900"
      : "";

  return <button className={clsx(base, variantClass, className)} {...props} />;
}

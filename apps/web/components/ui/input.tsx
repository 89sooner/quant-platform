import { clsx } from "clsx";
import type { DetailedHTMLProps, InputHTMLAttributes } from "react";

const base = "w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400";

export type InputProps = DetailedHTMLProps<InputHTMLAttributes<HTMLInputElement>, HTMLInputElement>;

export function Input({ className, ...props }: InputProps) {
  return <input className={clsx(base, className)} {...props} />;
}

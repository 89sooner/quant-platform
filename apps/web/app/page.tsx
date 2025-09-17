"use client";

import { useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { postBacktest } from "../lib/api";

type StrategyParams = {
  fast: number;
  slow: number;
  atr_mult_sl: number;
};

type BacktestState = {
  status: "idle" | "submitting" | "success" | "error";
  message?: string;
  jobId?: string;
};

const DEFAULT_PARAMS: StrategyParams = { fast: 12, slow: 26, atr_mult_sl: 2 };

const PARAM_FIELDS: Array<{
  key: keyof StrategyParams;
  label: string;
  min: number;
  step?: number;
}> = [
  { key: "fast", label: "Fast EMA", min: 1 },
  { key: "slow", label: "Slow EMA", min: 2 },
  { key: "atr_mult_sl", label: "ATR Stop Multiplier", min: 0, step: 0.1 }
];

function StrategyHeader() {
  return (
    <header className="space-y-2 text-center">
      <p className="text-sm uppercase tracking-wide text-slate-400">Quant Platform</p>
      <h1 className="text-3xl font-semibold text-slate-100">Configure and Backtest Strategies</h1>
      <p className="text-slate-400">Adjust parameters and enqueue a backtest job for the worker queue.</p>
    </header>
  );
}

function StatusMessage({ state }: { state: BacktestState }) {
  if (state.status === "success" && state.jobId) {
    return (
      <span>
        ✅ {state.message}: <code className="font-mono">{state.jobId}</code>
      </span>
    );
  }
  if (state.status === "error") {
    return <span>⚠️ {state.message}</span>;
  }
  return <span>Set parameters then enqueue a backtest.</span>;
}

function useBacktest() {
  const [name, setName] = useState("ema_crossover");
  const [params, setParams] = useState<StrategyParams>(DEFAULT_PARAMS);
  const [state, setState] = useState<BacktestState>({ status: "idle" });

  async function submit() {
    setState({ status: "submitting" });
    try {
      const payload = {
        class_name: `${name.replace(/[^A-Za-z0-9_]/g, "_")}_Auto`,
        dsl: {
          blocks: [
            { id: "ema_fast", type: "EMA", params: { period: params.fast } },
            { id: "ema_slow", type: "EMA", params: { period: params.slow } },
            { id: "cross", type: "CrossOver", inputs: ["ema_fast", "ema_slow"] },
            { id: "rule_long", type: "Rule", expr: "long: cross.up" },
            { id: "rule_exit", type: "Rule", expr: "exit_long: cross.down" }
          ],
          risk: { risk_per_trade: 0.01 },
          execution: {
            order_type: "limit",
            slippage_bps: 5,
            fee_bps: { maker: 1.0, taker: 5.0 }
          }
        },
        timeframe: "5m",
        exchange: "binance",
        pairs: ["BTC/USDT"],
        backtest: { start: "2024-01-01", end: "2025-06-30", cash: 10000 }
      };

      const result = await postBacktest(payload);
      setState({ status: "success", message: "Backtest enqueued", jobId: result.job_id });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setState({ status: "error", message });
    }
  }

  function updateParam(key: keyof StrategyParams, value: number) {
    setParams({ ...params, [key]: value });
  }

  return { name, setName, params, updateParam, state, submit };
}

function ParameterInput({
  id,
  label,
  value,
  min,
  step,
  onChange
}: {
  id: string;
  label: string;
  value: number;
  min: number;
  step?: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-300" htmlFor={id}>
        {label}
      </label>
      <Input
        id={id}
        type="number"
        value={value}
        min={min}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </div>
  );
}

function StrategyForm() {
  const { name, setName, params, updateParam, state, submit } = useBacktest();

  return (
    <Card className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-300" htmlFor="name">
            Strategy Name
          </label>
          <Input id="name" value={name} onChange={(event) => setName(event.target.value)} />
        </div>
        {PARAM_FIELDS.map((field) => (
          <ParameterInput
            key={field.key}
            id={field.key}
            label={field.label}
            value={params[field.key]}
            min={field.min}
            step={field.step}
            onChange={(value) => updateParam(field.key, value)}
          />
        ))}
      </section>

      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-400">
          <StatusMessage state={state} />
        </div>
        <Button disabled={state.status === "submitting"} onClick={submit}>
          {state.status === "submitting" ? "Submitting..." : "Run Backtest"}
        </Button>
      </div>
    </Card>
  );
}

export default function HomePage() {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 py-10">
      <StrategyHeader />
      <StrategyForm />
    </main>
  );
}

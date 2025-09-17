export type BacktestPayload = {
  class_name: string;
  dsl: unknown;
  timeframe: string;
  can_short?: boolean;
  exchange: string;
  pairs: string[];
  backtest: {
    start: string;
    end: string;
    cash: number;
  };
};

export async function postBacktest(payload: BacktestPayload) {
  const response = await fetch("/api/codegen-backtest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Failed to enqueue backtest: ${response.statusText}`);
  }

  return (await response.json()) as { job_id: string };
}

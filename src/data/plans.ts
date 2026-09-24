import planData from "./plans.json";

export interface Plan {
  plan_id: string;
  plan_name: string;
  audience: "individual" | "employer";
  program_service_fee: string;
  billing_interval: string;
  stripe_url: string;
  setup_fee_label?: string;
  setup_fee_amount?: string;
  setup_fee_url?: string;
  notes: string;
}

export const plans = planData as Plan[];

export function getSafePlans() {
  return plans.map(({ plan_id, plan_name, program_service_fee, billing_interval, audience, notes }) => ({
    plan_id,
    plan_name,
    program_service_fee,
    billing_interval,
    audience,
    notes,
  }));
}

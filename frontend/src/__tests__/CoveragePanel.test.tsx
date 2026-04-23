import { render, screen } from "@testing-library/react";
import { CoveragePanel } from "@/components/run/CoveragePanel";

test("shows current coverage percentage", () => {
  render(<CoveragePanel pct={73.5} target={90} history={[45, 73.5]} gaps={[]} />);
  expect(screen.getByText(/73\.5/)).toBeInTheDocument();
});

test("shows target coverage", () => {
  render(<CoveragePanel pct={73.5} target={90} history={[45, 73.5]} gaps={[]} />);
  expect(screen.getByText(/90/)).toBeInTheDocument();
});

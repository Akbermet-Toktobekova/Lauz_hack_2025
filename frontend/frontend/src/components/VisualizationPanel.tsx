import { FraudAnalysisResponse } from "@/types/fraud";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp, PieChart, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface VisualizationPanelProps {
  data: FraudAnalysisResponse | null;
}

/**
 * Right panel component - placeholder for future data visualizations
 * 
 * Extensibility points:
 * - Add chart libraries (recharts is already installed)
 * - Implement risk trend line charts
 * - Add transaction category pie charts
 * - Display geographic heatmaps
 * - Show time-series analysis
 */
export const VisualizationPanel = ({ data }: VisualizationPanelProps) => {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-sm">Visualizations will appear here after analysis</p>
          <p className="text-xs mt-2 text-muted-foreground">
            Use recharts library to create charts from analysis data
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Risk Score Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Risk Score Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Current Risk Score</span>
              <Badge variant="outline" className="text-lg font-bold">
                {data.risk_score}/100
              </Badge>
            </div>
            <div className="h-64 border-2 border-dashed border-border rounded-lg flex items-center justify-center bg-muted/30">
              <div className="text-center text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Risk trend chart will be implemented here</p>
                <p className="text-xs mt-1">
                  Use recharts to visualize risk score over time
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-foreground">Partner ID</span>
              <span className="font-mono text-xs text-muted-foreground">
                {data.partner_id.substring(0, 8)}...
              </span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-foreground">Risk Level</span>
              <Badge
                variant={
                  data.risk_score >= 70
                    ? "destructive"
                    : data.risk_score >= 40
                    ? "default"
                    : "secondary"
                }
              >
                {data.risk_score >= 70
                  ? "High"
                  : data.risk_score >= 40
                  ? "Medium"
                  : "Low"}
              </Badge>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-foreground">Analysis Date</span>
              <span className="text-xs text-muted-foreground">
                {new Date(data.timestamp).toLocaleDateString()}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Future Visualizations Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5 text-primary" />
            Future Visualizations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 border-2 border-dashed border-border rounded-lg flex items-center justify-center bg-muted/30">
            <div className="text-center text-muted-foreground">
              <Info className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Extend this panel with:</p>
              <ul className="text-xs mt-2 space-y-1 text-left">
                <li>• Transaction pattern charts</li>
                <li>• Geographic risk distribution</li>
                <li>• Time-series risk analysis</li>
                <li>• Comparative risk metrics</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

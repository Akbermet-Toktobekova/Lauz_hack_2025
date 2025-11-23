import { FraudAnalysisResponse } from "@/types/fraud";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";

interface AnalysisPanelProps {
  data: FraudAnalysisResponse | null;
}

/**
 * Determines risk level based on score (0-100 scale)
 */
const getRiskLevel = (score: number): "high" | "medium" | "low" => {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
};

/**
 * Gets risk badge color class
 */
const getRiskBadgeColor = (score: number) => {
  const level = getRiskLevel(score);
  if (level === "high") return "bg-red-600 text-white";
  if (level === "medium") return "bg-yellow-600 text-white";
  return "bg-green-600 text-white";
};

/**
 * Left panel component displaying fraud analysis text
 * Matches backend API response structure
 */
export const AnalysisPanel = ({ data }: AnalysisPanelProps) => {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>Submit a partner ID to view analysis results</p>
      </div>
    );
  }

  const riskLevel = getRiskLevel(data.risk_score);

  return (
    <div className="space-y-6">
      {/* Risk Score Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-sm font-normal">Partner ID:</span>
            <Badge variant="outline" className="font-mono text-xs">
              {data.partner_id.substring(0, 8)}...
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Risk Score</span>
              <Badge className={getRiskBadgeColor(data.risk_score)}>
                {data.risk_score}/100
              </Badge>
            </div>
            <Progress value={data.risk_score} className="h-2" />
            <p className="text-xs text-muted-foreground mt-2">
              Risk Level: <span className="font-medium capitalize">{riskLevel}</span>
            </p>
          </div>
          <div className="text-xs text-muted-foreground">
            Analysis generated: {new Date(data.timestamp).toLocaleString()}
          </div>
        </CardContent>
      </Card>

      {/* Risk Assessment Rationale */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Assessment Rationale</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap text-foreground leading-relaxed">
              {data.rationale}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Partner Profile */}
      {data.profile_text && (
        <Card>
          <CardHeader>
            <CardTitle>Partner Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap text-foreground leading-relaxed">
                {data.profile_text}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Raw LLM Response (Collapsible) */}
      {data.raw_response && (
        <Card>
          <Collapsible>
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                <CardTitle className="flex items-center justify-between text-sm">
                  <span>Raw LLM Response</span>
                  <ChevronDown className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent>
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto font-mono whitespace-pre-wrap">
                  {data.raw_response}
                </pre>
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}
    </div>
  );
};


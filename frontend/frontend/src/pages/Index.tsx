import { useState, useEffect } from "react";
import { QueryInput } from "@/components/QueryInput";
import { QueryHistory } from "@/components/QueryHistory";
import { AnalysisPanel } from "@/components/AnalysisPanel";
import { VisualizationPanel } from "@/components/VisualizationPanel";
import { QueryMessage, FraudAnalysisResponse } from "@/types/fraud";
import { analyzeFraudRisk, checkHealth } from "@/services/fraudApi";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Shield, CheckCircle2, XCircle } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

const Index = () => {
  const [messages, setMessages] = useState<QueryMessage[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<FraudAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<{ connected: boolean; error?: string } | null>(null);
  const { toast } = useToast();

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const health = await checkHealth();
        setBackendStatus({ connected: true });
      } catch (error) {
        setBackendStatus({
          connected: false,
          error: error instanceof Error ? error.message : "Unknown error",
        });
      }
    };
    checkBackendHealth();
  }, []);

  const handleQuery = async (partnerId: string) => {
    // Add user message
    const userMessage: QueryMessage = {
      id: Date.now().toString(),
      type: "user",
      content: `Assess risk for Partner ID: ${partnerId}`,
      timestamp: new Date(),
      partnerId: partnerId,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await analyzeFraudRisk(partnerId);
      
      // Add assistant response
      const assistantMessage: QueryMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: `Analysis complete for Partner ${result.partner_id.substring(0, 8)}... Risk score: ${result.risk_score}/100`,
        timestamp: new Date(),
        data: result,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setCurrentAnalysis(result);

      toast({
        title: "Analysis Complete",
        description: `Risk assessment generated for partner ${result.partner_id.substring(0, 8)}...`,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      
      // Add error message
      const errorMsg: QueryMessage = {
        id: (Date.now() + 1).toString(),
        type: "error",
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);

      toast({
        title: "Analysis Failed",
        description: errorMessage,
        variant: "destructive",
      });
      console.error("Analysis error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  UBS Fraud Compliance Analysis
                </h1>
                <p className="text-sm text-muted-foreground">
                  AI-powered fraud risk assessment tool
                </p>
              </div>
            </div>
            {backendStatus && (
              <Badge
                variant={backendStatus.connected ? "default" : "destructive"}
                className="flex items-center gap-1"
              >
                {backendStatus.connected ? (
                  <>
                    <CheckCircle2 className="h-3 w-3" />
                    Backend Connected
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3" />
                    Backend Disconnected
                  </>
                )}
              </Badge>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-12rem)]">
          {/* Left Section: Chat Interface */}
          <div className="lg:col-span-1 flex flex-col gap-4">
            <ScrollArea className="flex-1 pr-4">
              <QueryHistory messages={messages} />
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground mt-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Analyzing fraud risk...</span>
                </div>
              )}
            </ScrollArea>
            <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
          </div>

          {/* Right Section: Split Panel Results */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Analysis Text Panel */}
            <ScrollArea className="h-full pr-4">
              <AnalysisPanel data={currentAnalysis} />
            </ScrollArea>

            {/* Visualization Panel */}
            <ScrollArea className="h-full pr-4">
              <VisualizationPanel data={currentAnalysis} />
            </ScrollArea>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;

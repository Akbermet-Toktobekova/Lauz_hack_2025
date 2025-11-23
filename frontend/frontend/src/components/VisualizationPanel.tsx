import { FraudAnalysisResponse } from "@/types/fraud";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp, Receipt } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ChartContainer, ChartTooltip } from "@/components/ui/chart";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid } from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface VisualizationPanelProps {
  data: FraudAnalysisResponse | null;
}

/**
 * Right panel component for data visualizations
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

  // Prepare transaction data for the chart
  const prepareTransactionData = () => {
    // Use all_transactions if available, otherwise fall back to recent_transactions
    const transactions = data?.ucp?.all_transactions || data?.ucp?.recent_transactions || [];
    
    if (!transactions || transactions.length === 0) {
      return [];
    }

    // Group transactions by date and sum amounts for better visualization
    const dateMap = new Map<string, number>();
    
    transactions.forEach((tx) => {
      const dateStr = tx.Date || tx.date || tx['Transaction Date'];
      const amountVal = tx.Amount || tx.amount || tx['Transaction Amount'];
      
      if (!dateStr || amountVal === null || amountVal === undefined) {
        return;
      }
      
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        return;
      }
      
      const amount = typeof amountVal === 'number' ? amountVal : parseFloat(String(amountVal)) || 0;
      if (isNaN(amount)) {
        return;
      }
      
      // Format date as YYYY-MM-DD for grouping
      const dateKey = date.toISOString().split('T')[0];
      const currentTotal = dateMap.get(dateKey) || 0;
      dateMap.set(dateKey, currentTotal + Math.abs(amount));
    });

    // Convert to array and sort by date
    const processed = Array.from(dateMap.entries())
      .map(([dateKey, totalAmount]) => {
        const date = new Date(dateKey);
        return {
          date: dateKey,
          dateTime: date.getTime(),
          amount: totalAmount,
          dateLabel: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          shortLabel: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        };
      })
      .sort((a, b) => a.dateTime - b.dateTime);
    
    return processed;
  };

  const chartData = prepareTransactionData();
  const hasTransactions = chartData.length > 0;
  
  // Calculate statistics for display
  const totalSpending = chartData.reduce((sum, d) => sum + d.amount, 0);
  const avgSpending = chartData.length > 0 ? totalSpending / chartData.length : 0;
  const maxSpending = chartData.length > 0 ? Math.max(...chartData.map(d => d.amount)) : 0;

  // Get last 10 transactions for table display
  const getLast10Transactions = () => {
    const transactions = data?.ucp?.all_transactions || data?.ucp?.recent_transactions || [];
    
    if (!transactions || transactions.length === 0) {
      return [];
    }

    // Process and sort transactions by date (most recent first)
    const processed = transactions
      .map((tx) => {
        const dateStr = tx.Date || tx.date || tx['Transaction Date'];
        const amountVal = tx.Amount || tx.amount || tx['Transaction Amount'];
        const currency = tx.Currency || tx.currency || 'CHF';
        const debitCredit = tx['Debit/Credit'] || tx.debit_credit || tx['DebitCredit'] || '';
        const transferType = tx['Transfer_Type'] || tx.transfer_type || tx['TransferType'] || '';
        
        if (!dateStr || amountVal === null || amountVal === undefined) {
          return null;
        }
        
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
          return null;
        }
        
        const amount = typeof amountVal === 'number' ? amountVal : parseFloat(String(amountVal)) || 0;
        if (isNaN(amount)) {
          return null;
        }
        
        return {
          date: date,
          dateTime: date.getTime(),
          dateFormatted: date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }),
          amount: Math.abs(amount),
          currency: currency,
          debitCredit: debitCredit,
          transferType: transferType,
          raw: tx
        };
      })
      .filter((item): item is NonNullable<typeof item> => item !== null)
      .sort((a, b) => b.dateTime - a.dateTime) // Most recent first
      .slice(0, 10); // Get last 10
    
    return processed;
  };

  const last10Transactions = getLast10Transactions();

  return (
    <div className="space-y-6">
      {/* Risk Score Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            {hasTransactions ? "Spending Over Time" : "Risk Score Breakdown"}
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
            {hasTransactions && (
              <div className="space-y-4">
                {/* Statistics Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Total Spending</p>
                    <p className="text-lg font-semibold">{totalSpending.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Average Daily</p>
                    <p className="text-lg font-semibold">{avgSpending.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground mb-1">Peak Amount</p>
                    <p className="text-lg font-semibold">{maxSpending.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                  </div>
                </div>
                
                {/* Professional Line Chart with Area */}
                <div className="h-80">
                  <ChartContainer
                    config={{
                      spending: {
                        label: "Daily Spending",
                        color: "hsl(221.2 83.2% 53.3%)",
                      },
                    }}
                    className="h-full w-full"
                  >
                    <AreaChart
                      data={chartData}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="colorSpending" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="hsl(221.2 83.2% 53.3%)" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="hsl(221.2 83.2% 53.3%)" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.2} />
                      <XAxis
                        dataKey="shortLabel"
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => {
                          if (value >= 1000) {
                            return `${(value / 1000).toFixed(1)}k`;
                          }
                          return value.toString();
                        }}
                      />
                      <ChartTooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="rounded-lg border bg-background/95 backdrop-blur-sm p-3 shadow-lg">
                                <div className="grid gap-2">
                                  <div className="flex items-center justify-between gap-4">
                                    <span className="text-xs font-medium text-muted-foreground">Date</span>
                                    <span className="text-sm font-semibold">{data.dateLabel}</span>
                                  </div>
                                  <div className="flex items-center justify-between gap-4">
                                    <span className="text-xs font-medium text-muted-foreground">Amount</span>
                                    <span className="text-sm font-bold text-primary">
                                      {data.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="amount"
                        stroke="hsl(221.2 83.2% 53.3%)"
                        strokeWidth={2.5}
                        fill="url(#colorSpending)"
                        dot={{ fill: "hsl(221.2 83.2% 53.3%)", r: 3, strokeWidth: 2, stroke: "#fff" }}
                        activeDot={{ r: 5, strokeWidth: 2 }}
                      />
                    </AreaChart>
                  </ChartContainer>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Transactions Table */}
      {last10Transactions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5 text-primary" />
              Recent Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead>Currency</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {last10Transactions.map((tx, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">
                        {tx.dateFormatted}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-1">
                          <span className="text-sm">{tx.transferType || 'N/A'}</span>
                          {tx.debitCredit && (
                            <Badge 
                              variant={tx.debitCredit.toLowerCase() === 'debit' ? 'destructive' : 'default'}
                              className="w-fit text-xs"
                            >
                              {tx.debitCredit}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {tx.amount.toLocaleString('en-US', { 
                          minimumFractionDigits: 2, 
                          maximumFractionDigits: 2 
                        })}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {tx.currency}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

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

    </div>
  );
};

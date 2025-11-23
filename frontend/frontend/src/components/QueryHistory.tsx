import { QueryMessage } from "@/types/fraud";
import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface QueryHistoryProps {
  messages: QueryMessage[];
}

/**
 * Displays conversation history in chat format
 */
export const QueryHistory = ({ messages }: QueryHistoryProps) => {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">Start a fraud analysis query</p>
          <p className="text-sm mt-2">
            Ask about client risk profiles and transaction patterns
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-3",
            message.type === "user" ? "justify-end" : "justify-start"
          )}
        >
          {message.type === "assistant" && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
          )}
          <div
            className={cn(
              "max-w-[80%] rounded-lg px-4 py-3",
              message.type === "user"
                ? "bg-primary text-primary-foreground"
                : message.type === "error"
                ? "bg-destructive/10 border border-destructive text-destructive"
                : "bg-card border border-border"
            )}
          >
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            {message.data && (
              <div className="mt-2 text-xs opacity-70">
                <p>Risk Score: {message.data.risk_score}/100</p>
              </div>
            )}
            <p className="text-xs opacity-70 mt-2">
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>
          {message.type === "user" && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
              <User className="h-5 w-5 text-secondary-foreground" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

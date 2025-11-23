import { useState } from "react";
import { Send, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface QueryInputProps {
  onSubmit: (input: string, isQuestion: boolean) => void;
  isLoading: boolean;
  currentPartnerId?: string; // Track current partner in conversation
}

/**
 * Validates UUID format (basic validation)
 */
const isValidUUID = (id: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(id.trim());
};

/**
 * Detects if input is a Partner ID or a natural language question
 */
const isPartnerId = (input: string): boolean => {
  const trimmed = input.trim();
  // If it looks like a UUID, treat as Partner ID
  if (isValidUUID(trimmed)) {
    return true;
  }
  // If it's very short and contains only UUID-like characters, might be Partner ID
  if (trimmed.length < 10 && /^[0-9a-f-]+$/i.test(trimmed)) {
    return true;
  }
  // Otherwise, treat as a question
  return false;
};

/**
 * Query input component - supports both Partner IDs and natural language questions
 */
export const QueryInput = ({ onSubmit, isLoading, currentPartnerId }: QueryInputProps) => {
  const [input, setInput] = useState("");
  const [showValidation, setShowValidation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    
    if (!trimmed || isLoading) return;
    
    const isId = isPartnerId(trimmed);
    
    // If it looks like a Partner ID but isn't valid UUID, show warning
    if (isId && !isValidUUID(trimmed)) {
      setShowValidation(true);
    } else {
      setShowValidation(false);
    }
    
    onSubmit(trimmed, !isId);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isInvalid = input.trim() && isPartnerId(input) && !isValidUUID(input);
  const placeholder = currentPartnerId 
    ? "Ask a question about this customer or assess another partner..." 
    : "Ask anything: 'Assess risk for partner [ID]' or 'What is the name of client [ID]?'...";

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Input
            type="text"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              setShowValidation(false);
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`bg-card border-border focus:ring-primary ${
              isInvalid ? "border-destructive" : ""
            }`}
            disabled={isLoading}
          />
          {showValidation && isInvalid && (
            <Alert variant="destructive" className="mt-2">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                Partner ID should be in UUID format (e.g., 96a660ff-08e0-49c1-be6d-bb22a84e742e)
              </AlertDescription>
            </Alert>
          )}
          {currentPartnerId && (
            <p className="text-xs text-muted-foreground mt-1">
              Currently analyzing: {currentPartnerId.substring(0, 8)}...
            </p>
          )}
        </div>
        <Button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
};


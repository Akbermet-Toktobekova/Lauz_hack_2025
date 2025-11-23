import { useState } from "react";
import { Send, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface QueryInputProps {
  onSubmit: (partnerId: string) => void;
  isLoading: boolean;
}

/**
 * Validates UUID format (basic validation)
 */
const isValidUUID = (id: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(id.trim());
};

/**
 * Query input component for submitting partner ID for fraud analysis
 */
export const QueryInput = ({ onSubmit, isLoading }: QueryInputProps) => {
  const [partnerId, setPartnerId] = useState("");
  const [showValidation, setShowValidation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedId = partnerId.trim();
    
    if (!trimmedId || isLoading) return;
    
    // Allow submission even if not perfect UUID (backend will validate)
    // But show warning if format looks wrong
    if (!isValidUUID(trimmedId)) {
      setShowValidation(true);
      // Still allow submission - backend will handle validation
    } else {
      setShowValidation(false);
    }
    
    onSubmit(trimmedId);
    setPartnerId("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isInvalid = partnerId.trim() && !isValidUUID(partnerId);

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Input
            type="text"
            value={partnerId}
            onChange={(e) => {
              setPartnerId(e.target.value);
              setShowValidation(false);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Enter Partner ID (UUID format)"
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
        </div>
        <Button
          type="submit"
          disabled={!partnerId.trim() || isLoading}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
};


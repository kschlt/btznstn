# Component Guidelines

## Overview

Guidelines for implementing UI components using Shadcn/ui + Tailwind CSS. These patterns ensure consistency, accessibility, and AI-friendly implementation.

---

## Component Installation

### Adding Shadcn Components

```bash
# Install components as needed
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add select
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add label
```

**Result:** Components copied to `components/ui/`

---

## Core Components

### Button

**Usage:**
```tsx
import { Button } from "@/components/ui/button"

// Primary action
<Button>Zustimmen</Button>

// Secondary action
<Button variant="secondary">Abbrechen</Button>

// Destructive action
<Button variant="destructive">Ablehnen</Button>

// With icon
<Button>
  <CheckIcon className="mr-2 h-4 w-4" />
  Bestätigen
</Button>

// Loading state
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Wird geladen...
</Button>
```

**Mobile requirements:**
```tsx
<Button className="min-h-tap min-w-tap">
  {/* Ensures 44px minimum tap target */}
</Button>
```

---

### Card

**Booking Card Pattern:**
```tsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface BookingCardProps {
  booking: {
    id: string
    requester_first_name: string
    party_size: number
    status: "Pending" | "Confirmed" | "Denied"
    affiliation: "Ingeborg" | "Cornelia" | "Angelika"
  }
}

export function BookingCard({ booking }: BookingCardProps) {
  return (
    <Card
      className={cn(
        "min-h-tap cursor-pointer transition-shadow hover:shadow-md",
        // Affiliation border
        booking.affiliation === "Ingeborg" && "border-l-4 border-l-affiliation-ingeborg",
        booking.affiliation === "Cornelia" && "border-l-4 border-l-affiliation-cornelia",
        booking.affiliation === "Angelika" && "border-l-4 border-l-affiliation-angelika"
      )}
    >
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">
          {booking.requester_first_name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm">
          <p className="text-muted-foreground">{booking.party_size} Personen</p>
          <Badge
            variant={
              booking.status === "Confirmed" ? "success" :
              booking.status === "Denied" ? "destructive" :
              "secondary"
            }
          >
            {booking.status === "Pending" && "Ausstehend"}
            {booking.status === "Confirmed" && "Bestätigt"}
            {booking.status === "Denied" && "Abgelehnt"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

### Dialog

**Usage Pattern:**
```tsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function CreateBookingDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Neue Anfrage</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Neue Buchungsanfrage</DialogTitle>
          <DialogDescription>
            Wähle einen Zeitraum und fülle die Details aus.
          </DialogDescription>
        </DialogHeader>
        {/* Form content */}
      </DialogContent>
    </Dialog>
  )
}
```

---

### Form

**React Hook Form + Zod Pattern:**
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const bookingFormSchema = z.object({
  requester_first_name: z.string().min(1, "Dieses Feld wird benötigt.").max(40),
  requester_email: z.string().email("Bitte gib eine gültige E-Mail-Adresse an."),
  start_date: z.date(),
  end_date: z.date(),
  party_size: z.number().int().min(1).max(10),
  affiliation: z.enum(["Ingeborg", "Cornelia", "Angelika"]),
  description: z.string().max(500).optional(),
})

type BookingFormData = z.infer<typeof bookingFormSchema>

export function BookingForm() {
  const form = useForm<BookingFormData>({
    resolver: zodResolver(bookingFormSchema),
    defaultValues: {
      party_size: 1,
    },
  })

  async function onSubmit(data: BookingFormData) {
    // API call
    await createBooking(data)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="requester_first_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Vorname</FormLabel>
              <FormControl>
                <Input placeholder="Anna" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="requester_email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>E-Mail</FormLabel>
              <FormControl>
                <Input type="email" placeholder="anna@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Other fields... */}

        <Button type="submit" className="w-full">
          Anfrage senden
        </Button>
      </form>
    </Form>
  )
}
```

---

### Select

**Affiliation Selector:**
```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

<FormField
  control={form.control}
  name="affiliation"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Zugehörigkeit</FormLabel>
      <Select onValueChange={field.onChange} defaultValue={field.value}>
        <FormControl>
          <SelectTrigger>
            <SelectValue placeholder="Wähle eine Zugehörigkeit" />
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem value="Ingeborg">Ingeborg</SelectItem>
          <SelectItem value="Cornelia">Cornelia</SelectItem>
          <SelectItem value="Angelika">Angelika</SelectItem>
        </SelectContent>
      </Select>
      <FormMessage />
    </FormItem>
  )}
/>
```

---

### Calendar

**Date Picker:**
```tsx
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { de } from "date-fns/locale"

<FormField
  control={form.control}
  name="start_date"
  render={({ field }) => (
    <FormItem className="flex flex-col">
      <FormLabel>Startdatum</FormLabel>
      <Popover>
        <PopoverTrigger asChild>
          <FormControl>
            <Button
              variant="outline"
              className={cn(
                "w-full pl-3 text-left font-normal",
                !field.value && "text-muted-foreground"
              )}
            >
              {field.value ? (
                format(field.value, "PPP", { locale: de })
              ) : (
                <span>Datum wählen</span>
              )}
              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
            </Button>
          </FormControl>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={field.value}
            onSelect={field.onChange}
            locale={de}
            disabled={(date) => date < new Date()}
            initialFocus
          />
        </PopoverContent>
      </Popover>
      <FormMessage />
    </FormItem>
  )}
/>
```

---

### Badge

**Status Badge:**
```tsx
import { Badge } from "@/components/ui/badge"

// Status-specific styling
function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "Confirmed" ? "success" :
    status === "Denied" ? "destructive" :
    "secondary"

  const text =
    status === "Pending" ? "Ausstehend" :
    status === "Confirmed" ? "Bestätigt" :
    status === "Denied" ? "Abgelehnt" :
    status === "Canceled" ? "Storniert" :
    status

  return <Badge variant={variant}>{text}</Badge>
}
```

**Custom Badge Variants (add to `components/ui/badge.tsx`):**
```tsx
const badgeVariants = cva(
  "...",
  {
    variants: {
      variant: {
        default: "...",
        secondary: "...",
        destructive: "...",
        outline: "...",
        success: "bg-green-100 text-green-800 hover:bg-green-200",  // Add this
      },
    },
  }
)
```

---

## Layout Patterns

### Responsive Container

```tsx
<div className="container mx-auto px-4 sm:px-6 md:px-8 lg:px-12">
  {/* Content */}
</div>
```

### Mobile-First Grid

```tsx
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {bookings.map(booking => (
    <BookingCard key={booking.id} booking={booking} />
  ))}
</div>
```

### Sticky Header

```tsx
<header className="sticky top-0 z-30 bg-background border-b">
  <div className="container mx-auto px-4 py-3">
    <h1 className="text-2xl font-bold">Betzenstein Kalender</h1>
  </div>
</header>
```

---

## Accessibility Patterns

### Skip to Content

```tsx
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground"
>
  Zum Hauptinhalt springen
</a>

<main id="main-content">
  {/* Content */}
</main>
```

### Aria Labels

```tsx
<Button aria-label="Buchung von Anna anzeigen">
  <EyeIcon className="h-4 w-4" />
</Button>
```

### Loading States

```tsx
<div role="status" aria-live="polite">
  {isLoading ? "Wird geladen..." : "Fertig"}
</div>
```

---

## Related Documentation

- [Design Tokens](design-tokens.md)
- [UI Screens](../specification/ui-screens.md)
- [ADR-005: UI Framework](../architecture/adr-005-ui-framework.md)

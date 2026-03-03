/**
 * Tipos e interfaces do módulo de vendas
 * Fluxo: Orçamento → Pedido → Faturamento
 */

export interface Product {
  id: string;
  name: string;
  basePrice: number;
  category: string;
  minQuantity?: number;
}

export interface DiscountRule {
  id: string;
  name: string;
  type: 'percentage' | 'fixed' | 'tiered';
  value: number;
  minAmount?: number;
  minQuantity?: number;
  applicableCategories?: string[];
  validFrom: Date;
  validTo: Date;
  active: boolean;
}

export interface QuoteItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  subtotal: number;
}

export interface Quote {
  id: string;
  customerId: string;
  customerName: string;
  items: QuoteItem[];
  subtotal: number;
  totalDiscount: number;
  total: number;
  validityDate: Date;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'expired' | 'converted';
  createdAt: Date;
  updatedAt: Date;
  notes?: string;
}

export interface OrderItem {
  quoteItemId: string;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  subtotal: number;
}

export interface Order {
  id: string;
  quoteId?: string;
  customerId: string;
  customerName: string;
  items: OrderItem[];
  subtotal: number;
  totalDiscount: number;
  total: number;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  paymentStatus: 'pending' | 'partial' | 'paid';
  createdAt: Date;
  updatedAt: Date;
  shippingAddress?: string;
  notes?: string;
}

export interface InvoiceItem {
  orderId: string;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
}

export interface Invoice {
  id: string;
  orderId: string;
  customerId: string;
  customerName: string;
  items: InvoiceItem[];
  subtotal: number;
  taxes: number;
  total: number;
  status: 'draft' | 'issued' | 'paid' | 'overdue' | 'cancelled';
  dueDate: Date;
  issuedDate: Date;
  paymentTerms: number; // dias para pagamento
  createdAt: Date;
  updatedAt: Date;
}

export interface PricingResult {
  basePrice: number;
  appliedDiscounts: AppliedDiscount[];
  totalDiscount: number;
  finalPrice: number;
}

export interface AppliedDiscount {
  ruleId: string;
  ruleName: string;
  discountAmount: number;
  reason: string;
}

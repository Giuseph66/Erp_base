/**
 * Regras de preço e descontos do módulo de vendas
 */

import {
  Product,
  DiscountRule,
  PricingResult,
  AppliedDiscount,
} from './types';

export class PricingEngine {
  private products: Map<string, Product>;
  private discountRules: DiscountRule[];

  constructor() {
    this.products = new Map();
    this.discountRules = [];
  }

  /**
   * Registra um produto no catálogo
   */
  registerProduct(product: Product): void {
    this.products.set(product.id, product);
  }

  /**
   * Registra uma regra de desconto
   */
  registerDiscountRule(rule: DiscountRule): void {
    this.discountRules.push(rule);
  }

  /**
   * Obtém um produto pelo ID
   */
  getProduct(productId: string): Product | undefined {
    return this.products.get(productId);
  }

  /**
   * Calcula o preço com descontos aplicáveis
   */
  calculatePrice(
    productId: string,
    quantity: number,
    customerCategory?: string
  ): PricingResult {
    const product = this.products.get(productId);
    if (!product) {
      throw new Error(`Produto não encontrado: ${productId}`);
    }

    const basePrice = product.basePrice * quantity;
    const appliedDiscounts: AppliedDiscount[] = [];
    const now = new Date();

    // Filtra regras ativas e válidas
    const applicableRules = this.discountRules.filter((rule) => {
      if (!rule.active) return false;
      if (now < rule.validFrom || now > rule.validTo) return false;

      // Verifica categoria
      if (
        rule.applicableCategories &&
        rule.applicableCategories.length > 0 &&
        customerCategory &&
        !rule.applicableCategories.includes(customerCategory)
      ) {
        return false;
      }

      // Verifica quantidade mínima
      if (rule.minQuantity && quantity < rule.minQuantity) {
        return false;
      }

      return true;
    });

    let totalDiscount = 0;
    let currentAmount = basePrice;

    for (const rule of applicableRules) {
      let discountAmount = 0;

      // Verifica valor mínimo para aplicação
      if (rule.minAmount && currentAmount < rule.minAmount) {
        continue;
      }

      switch (rule.type) {
        case 'percentage':
          discountAmount = currentAmount * (rule.value / 100);
          break;
        case 'fixed':
          discountAmount = rule.value;
          break;
        case 'tiered':
          discountAmount = this.calculateTieredDiscount(
            rule.value,
            quantity,
            currentAmount
          );
          break;
      }

      if (discountAmount > 0) {
        appliedDiscounts.push({
          ruleId: rule.id,
          ruleName: rule.name,
          discountAmount,
          reason: this.getDiscountReason(rule, quantity),
        });
        totalDiscount += discountAmount;
        currentAmount -= discountAmount;
      }
    }

    // Garante que o desconto não ultrapasse o valor total
    totalDiscount = Math.min(totalDiscount, basePrice);
    const finalPrice = Math.max(0, basePrice - totalDiscount);

    return {
      basePrice,
      appliedDiscounts,
      totalDiscount,
      finalPrice,
    };
  }

  /**
   * Calcula desconto escalonado (tiered)
   */
  private calculateTieredDiscount(
    tiers: number,
    quantity: number,
    amount: number
  ): number {
    // Exemplo: 5% para 10+ unidades, 10% para 50+ unidades, 15% para 100+ unidades
    const tierPercentages = [5, 10, 15];
    const tierQuantities = [10, 50, 100];

    let applicablePercentage = 0;
    for (let i = tierQuantities.length - 1; i >= 0; i--) {
      if (quantity >= tierQuantities[i]) {
        applicablePercentage = tierPercentages[i];
        break;
      }
    }

    return amount * (applicablePercentage / 100);
  }

  /**
   * Gera descrição do motivo do desconto
   */
  private getDiscountReason(rule: DiscountRule, quantity: number): string {
    const reasons: string[] = [];

    if (rule.minQuantity) {
      reasons.push(`Quantidade: ${quantity} un.`);
    }
    if (rule.applicableCategories) {
      reasons.push(`Categorias: ${rule.applicableCategories.join(', ')}`);
    }

    return reasons.length > 0 ? reasons.join(' | ') : 'Desconto padrão';
  }

  /**
   * Calcula o total de um pedido com múltiplos itens
   */
  calculateOrderTotal(
    items: Array<{ productId: string; quantity: number }>
  ): {
    subtotal: number;
    totalDiscount: number;
    total: number;
    itemsPricing: Array<{ productId: string; pricing: PricingResult }>;
  } {
    let subtotal = 0;
    let totalDiscount = 0;
    const itemsPricing: Array<{ productId: string; pricing: PricingResult }> =
      [];

    for (const item of items) {
      const pricing = this.calculatePrice(item.productId, item.quantity);
      subtotal += pricing.basePrice;
      totalDiscount += pricing.totalDiscount;
      itemsPricing.push({ productId: item.productId, pricing });
    }

    return {
      subtotal,
      totalDiscount,
      total: subtotal - totalDiscount,
      itemsPricing,
    };
  }
}

/**
 * Instância singleton do engine de preços
 */
export const pricingEngine = new PricingEngine();

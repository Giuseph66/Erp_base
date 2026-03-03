import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { Supplier } from './supplier.entity';

export enum PayableStatus {
  PENDING = 'pending',
  PARTIALLY_PAID = 'partially_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
}

@Entity('accounts_payable')
@Index(['supplierId', 'dueDate'])
@Index(['status', 'dueDate'])
export class AccountsPayable {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ length: 200 })
  description: string;

  @Column('decimal', { precision: 12, scale: 2 })
  totalAmount: number;

  @Column('decimal', { precision: 12, scale: 2, default: 0 })
  paidAmount: number;

  @Column('decimal', { precision: 12, scale: 2, nullable: true })
  discount: number;

  @Column('decimal', { precision: 12, scale: 2, nullable: true })
  interest: number;

  @Column({ type: 'date' })
  dueDate: Date;

  @Column({ type: 'date', nullable: true })
  paymentDate: Date;

  @Column({
    type: 'enum',
    enum: PayableStatus,
    default: PayableStatus.PENDING,
  })
  status: PayableStatus;

  @Column({ nullable: true })
  supplierId: string;

  @ManyToOne(() => Supplier, { nullable: true })
  @JoinColumn({ name: 'supplierId' })
  supplier: Supplier;

  @Column({ nullable: true })
  categoryId: string;

  @Column({ length: 100, nullable: true })
  documentNumber: string;

  @Column({ length: 500, nullable: true })
  notes: string;

  @Column({ default: false })
  isRecurring: boolean;

  @Column({ nullable: true })
  recurringPattern: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

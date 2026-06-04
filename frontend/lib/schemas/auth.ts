import { z } from "zod"

import { validatePassword } from "@/lib/auth/password-validation"

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

export type LoginFormValues = z.infer<typeof loginSchema>

export const registerSchema = z
  .object({
    email: z.string().email("Invalid email address"),
    password: z.string().superRefine((val, ctx) => {
      const error = validatePassword(val)

      if (error) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: error,
        })
      }
    }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  })

export type RegisterFormValues = z.infer<typeof registerSchema>

export const forgotPasswordSchema = z.object({
  email: z.string().email("Invalid email address"),
})

export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>

export const resetPasswordSchema = z
  .object({
    password: z.string().superRefine((val, ctx) => {
      const error = validatePassword(val)

      if (error) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: error,
        })
      }
    }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  })

export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>

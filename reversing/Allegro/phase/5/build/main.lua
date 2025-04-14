function H(a, b, c)
   if c < 0 then
      for i = 1, -c do
         a = a - b
      end
   else
      for i = 1, c do
         a = a + b
      end
   end
   return a
end

function G(A)
   local B = {}
   for j = 1, #A[1] do
      B[j] = {}
      for i = 1, #A do
         B[j][i] = A[i][j]
      end
   end
   return B
end

function F(A, B)
   local C = {}
   for i = 1, #A do
      C[i] = {}
      for j = 1, #A do
         C[i][j] = 0
         for k = 1, #A do
            C[i][j] = H(C[i][j], A[i][k], B[k][j])
         end
      end
   end
   return C
end

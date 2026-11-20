/* A PROGRAM THAT COMPUTES THE FACTORIAL
   for a user provided input
   AND PRINT THE RESULT ON STDOUT
*/

#include <stdio.h>

unsigned long COMPUTE(unsigned long);

int main()
{
    unsigned long NUMBER; /* USER input */
    printf("Please ENTER a Nonnegative Integer Value: ");
    scanf("%ld", &NUMBER);
    printf("The FACTORIAL of %ld IS %ld\n", NUMBER, COMPUTE(NUMBER));
    return 1;
}

unsigned long COMPUTE(unsigned long Number)
{
    return (Number > 0) ? (Number * COMPUTE(Number - 1)) : 1;
}

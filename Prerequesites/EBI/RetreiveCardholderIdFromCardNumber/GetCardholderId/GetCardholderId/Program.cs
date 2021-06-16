using Honeywell.Server.Cms.CardholderServicesClient;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GetCardholderId
{
    class Program
    {
        static void Main(string[] args)
        {
            var cardNumber = "1234";
            using (var cards = new CardsClient())
            {
                var cardholderId = cards.GetCardholderId(cardNumber, 0);

                if (cardholderId > 0)
                {
                    Console.WriteLine("Cardholder " + cardholderId.ToString() + " has card " + cardNumber);
                }
                else
                {
                    Console.WriteLine("Card " + cardNumber + " is unissued.");
                }
            }


        }
    }
}

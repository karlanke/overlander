using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;

namespace CameraServer.Hubs
{
    public class CameraHub : Hub
    {
        public async Task SendMessage(string user, string message)
        {
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
}
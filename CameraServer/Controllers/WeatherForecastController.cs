﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace CameraServer.Controllers
{
    [ApiController]
    [Route("")]
    public class CameraController : ControllerBase
    {


        [HttpGet]
        public string Get()
        {
            return "Hello, world!";
        }
    }
}
